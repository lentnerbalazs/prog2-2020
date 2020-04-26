import json
import pandas as pd
from sklearn.neighbors import KDTree

df = pd.read_pickle("filtered.pkl")
input_df = pd.read_json("inputs.json")
answers = [{"missing": True}] * input_df.shape[0]

for i in range(0, input_df.shape[0]):
    df_filt = df.loc[
        (input_df["stars"][i] == df["stars"])
        & (input_df["min_price"][i] < df["price"])
        & (df["price"] < input_df["max_price"][i])
    ]
    try:
        tree = KDTree(df_filt[["lon", "lat"]].values, leaf_size=5)
        answers[i] = df_filt.iloc[
            int(
                tree.query(
                    input_df[["lon", "lat"]].values[i].reshape(1, -1), k=1
                )[1]
            )
        ].to_dict()
    except:
        None

json.dump(answers, open("outputs.json", "w"))
