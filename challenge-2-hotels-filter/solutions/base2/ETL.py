import pandas as pd
import pickle

data_file_path = "data.csv"

df = pd.read_csv(data_file_path)

df_filtered = df.drop_duplicates().assign(
    price=lambda _df: _df["current-price"]
    .str[1:]
    .str.replace(",", "")
    .astype(float)
).loc[:, ["lon", "lat", "name", "stars", "price"]]\
 .sort_values("price")

star_dict = {}

for _gid, _gdf in df_filtered.groupby("stars"):
    star_dict[_gid] = _gdf.values

pickle.dump(star_dict, open("sd.pkl", "wb"))
