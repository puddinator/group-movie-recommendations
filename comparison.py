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
df.dropna(inplace = True)
df = df.groupby("user_id").filter(lambda x: len(x) > 30 )
df['difference'] = abs(df['rating_letterboxd'] - df['rating_user'])


mean = df.groupby("user_id")["difference"].mean()
mean_sorted = mean.sort_values(ascending=True)
# Not sure if a bug, but might need .reset_index()
print(mean_sorted)

mean_sorted.to_csv('data/test_ratings.csv')