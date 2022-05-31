import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

MINIMUM_MATCHES = 80


def merge_for_comparison(self, reviewed_movies_all, number_of_accounts, usernames):
    # Open csv files into Dataframe, nrows=1000000 to troubleshot
    df_ratings = pd.read_csv('data/ratings.csv', index_col=False, nrows=1000000)
    
    counter = 1
    first_time = True
    df_score_merged = pd.DataFrame()

    for reviewed_movies in reviewed_movies_all:
        self.update_state(state='PROGRESS', meta={'status': 'Calculating ' + usernames['username_' + str(counter)] + "'s movie scores"})

        df_my_ratings = pd.DataFrame(reviewed_movies)

        # Merge on where movie_id are same
        df_merged = df_ratings.merge(df_my_ratings, left_on="movie_id", right_on="movie_id", how='left', suffixes=('_letterboxd', '_user'))

        # Filter out data samples with insufficient movie matches
        df_merged = df_merged.groupby("user_id", sort=False).filter(lambda x: x['rating_user'].count() > MINIMUM_MATCHES)

        # Drop nan in order to calculate mean
        df_merged_dropped = df_merged.dropna()
        # Calculate differences in ratings

        df_merged_dropped['difference'] = abs(df_merged_dropped['rating_letterboxd'] - df_merged_dropped['rating_user'])

        ''' Consider using transform to optimize code?'''

        # Calculate mean difference
        df_compatibility = df_merged_dropped.groupby("user_id", as_index=False, sort=False)['difference'].mean()
        # Sorting is with .sort_values(ascending=True)

        # Calculate similarity
        df_compatibility['similarity'] = 100 - df_compatibility['difference']

        # This arbitrarily increases the impact of weighing
        df_compatibility['similarity'] = abs((df_compatibility['similarity'] - 60)) * 2

        # Drops rated movies (not NaN) and groups it back
        df_weighted_movies = df_merged[df_merged['rating_user'].isnull()].merge(df_compatibility,  left_on="user_id", right_on="user_id")
        df_weighted_movies['weighted_rating'] = df_weighted_movies['rating_letterboxd'] * df_weighted_movies['similarity']

        df_suggestion_group = df_weighted_movies.groupby("movie_id")
        df_weighted_movies['score_' + str(counter)] = df_suggestion_group.weighted_rating.transform(sum) / df_suggestion_group.similarity.transform(sum)

        df_score = df_weighted_movies.groupby('movie_id', as_index=False).filter(lambda x: x['score_' + str(counter)].count() > MINIMUM_MATCHES)[['movie_id', 'score_' + str(counter)]].drop_duplicates()
        
        self.update_state(state='PROGRESS', meta={'status': "Calculated!"})

        counter += 1

        if first_time == True:
            df_score_merged = df_score.copy()
            first_time = False
        else:
            df_score_merged = df_score_merged.merge(df_score, left_on="movie_id", right_on="movie_id")

    self.update_state(state='PROGRESS', meta={'status': 'Calculating combined movie scores'})

    # Calculate mean score and sort
    df_score_merged['mean_score'] = df_score_merged.iloc[:, 1:1 + number_of_accounts].mean(axis=1)
    df_score_merged = df_score_merged.sort_values(by='mean_score', ascending=False)

    df_movie_info = pd.read_csv('data/movie_data.csv', index_col=False)

    # genres image_url movie_id movie_title year_released vote_average vote_count ||  _id tbc
    df_movie_info_merge = df_movie_info.merge(df_score_merged.head(100), left_on="movie_id", right_on="movie_id").sort_values(by='mean_score', ascending=False)
    # df_movie_info_merge.to_csv('data/test_ratings.csv', index=False)
    # print(df_movie_info_merge)
    return df_movie_info_merge.to_json(orient='table', index=False)