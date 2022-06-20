import time 
from operator import index
import numpy as np
import pandas as pd

pd.options.mode.chained_assignment = None  # default='warn'

# To test speed
# start = time.process_time()
# print(time.process_time() - start)
        

def merge_for_comparison(self, reviewed_movies_all, usernames, number_of_accounts, fast, is_imdb):

    df_ratings = pd.read_parquet('data/ratings.parquet')
    # if (fast == True):
    #     df_ratings = df_ratings[:int(len(df_ratings.index) / 2)]
    df_movie_info = pd.read_parquet('data/movies.parquet')

    counter = 0
    first_time = True
    df_score_merged = pd.DataFrame()

    for reviewed_movies in reviewed_movies_all:
        MINIMUM_MATCHES = len(reviewed_movies) / 2
        MINIMUM_MATCHES_2 = 50 + len(reviewed_movies) / 10
        if (MINIMUM_MATCHES_2 > 80): MINIMUM_MATCHES_2 = 80
        
        if (is_imdb == True):
            self.update_state(state='PROGRESS', meta={'status': 'Calculating ' + usernames[counter].split("ur")[1].split("/")[0] + "'s movie scores"})
            df_merged = (
                pd.DataFrame(reviewed_movies)
                # Merge on where movie_id are same
                .merge(
                    df_ratings, 
                    left_on="imdb_id", 
                    right_on="imdb_id", 
                    how='right', 
                    suffixes=('_user', '_letterboxd')
                )
            )
        else:
            self.update_state(state='PROGRESS', meta={'status': 'Calculating ' + usernames[counter] + "'s movie scores"})
            df_merged = (
                pd.DataFrame(reviewed_movies)
                # Merge on where movie_id are same
                .merge(
                    df_ratings, 
                    left_on="movie_id", 
                    right_on="movie_id", 
                    how='right', 
                    suffixes=('_user', '_letterboxd')
                )
            )
        # Filter out other reviewers with insufficient movie matches
        # During the count it creates a copy, causing count number to double (?)

        # df_merged = df_merged[df_merged.groupby('user_id')['rating_user'].transform('count') >= MINIMUM_MATCHES * 2]

        df_compatibility = (
            # Drop nan in order to calculate mean
            df_merged.dropna()
            # Calculate differences in ratings
            .assign(difference = lambda x: abs(x['rating_letterboxd'] - x['rating_user']))
            # Calculate mean difference
            .groupby("user_id", as_index=False, sort=False)['difference'].mean()
            # Calculate similarity
            .assign(similarity = lambda x: 100 - x['difference'])
            # Find reviewers who are very similar in taste
            .assign(similarity = lambda x: ((abs(x['similarity'] - 85.0) + (x['similarity'] - 85.0)) / 2) ** 2)
        )
        
        df_weighted_movies = (
            # Drops rated movies (not NaN) and groups it back
            df_merged[df_merged['rating_user'].isnull()].merge(
                df_compatibility,  
                left_on="user_id", 
                right_on="user_id"
            )
            .assign(weighted_rating = lambda x: x['rating_letterboxd'] * x['similarity'])
        )

        df_suggestion_group = df_weighted_movies.groupby("movie_id")
        df_weighted_movies['score_' + str(counter)] = df_suggestion_group.weighted_rating.transform(sum) / df_suggestion_group.similarity.transform(sum)
        
        df_score = (
            # Filter out those with insufficient number of ratings
            df_weighted_movies[df_weighted_movies.groupby('movie_id')['movie_id'].transform('size') >= MINIMUM_MATCHES_2]
            # Drop the excess and get just movie_id and score_x
            .drop_duplicates(subset=['movie_id'])[['movie_id', 'score_' + str(counter)]]
        )
        
        counter += 1

        if first_time == True:
            df_score_merged = df_score.copy()
            first_time = False
        else:
            df_score_merged = df_score_merged.merge(df_score, left_on="movie_id", right_on="movie_id")

    df_movie_info_merge = (
        # Calculate mean score
        df_score_merged.assign(mean_score = lambda x: x.iloc[:, 1:1 + number_of_accounts].mean(axis=1))
        # Sort and extract top few
        .sort_values(by='mean_score', ascending=False)
        .head(10000)
        # Merge with movie db
        .merge(df_movie_info, left_on="movie_id", right_on="movie_id")
    )

    # df_movie_info_merge.to_csv('data/test_ratings.csv', index=False)
    # print(df_movie_info_merge)
    return df_movie_info_merge.to_json(orient='table', index=False)