import pandas as pd
from joblib import dump
from sklearn.neighbors import KDTree

data_file_path = "data.csv"

df = pd.read_csv(data_file_path)
df = df.drop_duplicates().assign(
    price=lambda _df: _df["current-price"]
    .str[1:]
    .str.replace(",", "")
    .astype(float)
).loc[:, ["lon", "lat", "name", "stars", "price"]]
sample_df = pd.DataFrame()
sample_df['stars']=list(df['stars'].unique())
df_list=[]



for i in range(len(sample_df)):
        sub_df=df[df['stars']==sample_df.loc[i, 'stars']]
        sub_df=sub_df.sort_values(by=['price'])
        sub_df['latsq']=sub_df['lat']*sub_df['lat']
        sub_df['lonsq']=sub_df['lon']*sub_df['lon']


        df_list.append(sub_df)

sample_df['data']=df_list
sample_df=sample_df.set_index('stars')
sample_df.to_pickle("filtered.pkl")
