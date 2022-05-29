import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

MINIMUM_MATCHES = 100

def merge_for_comparison(reviewed_movies):
    # Open csv files into Dataframe, nrows=1000000 to troubleshot
    df_ratings = pd.read_csv('data/ratings.csv', index_col=False)
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
    df_weighted_movies['score'] = df_suggestion_group.weighted_rating.transform(sum) / df_suggestion_group.similarity.transform(sum)

    score = df_weighted_movies.groupby('movie_id', as_index=False).filter(lambda x: x['score'].count() > MINIMUM_MATCHES)[['movie_id', 'score']].drop_duplicates().sort_values(by='score', ascending=False)

    print(score)

    score.to_csv('data/test_ratings.csv')

    return score