# df = pd.read_csv('data/raw_ratings.csv', index_col=False)

# df = df.drop(columns=['_id'])
# df = df[['user_id', 'movie_id', 'rating']]
# df["rating"] = 10 * df["rating"]

# df.to_csv('data/ratings.csv', index=False)

import numpy as np
import pandas as pd

df1 = pd.read_csv('data/ratings.csv', index_col=False)
df2 = pd.read_csv('data/my_ratings.csv', index_col=False)

df = df1.merge(df2, left_on="movie_id", right_on="movie_id", how='left', suffixes=('_letterboxd', '_user'))
df['difference'] = abs(df['rating_letterboxd'] - df['rating_user'])
# mean = df.loc[(df['user_id'] == 'turnitip') & (~(np.isnan(df["difference"])))].mean()
mean = df.loc[~(np.isnan(df["difference"]))].groupby("user_id")["difference"].mean()
mean_sorted = mean.sort_values
print(mean_sorted)
print(df)

df.to_csv('data/test_ratings.csv', index=False)