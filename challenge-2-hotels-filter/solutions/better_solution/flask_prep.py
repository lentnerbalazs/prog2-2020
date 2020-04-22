import json
from collections import defaultdict
from dataclasses import dataclass

import pandas as pd
import numpy as np
from flask import Flask
from flask import request
from flask import current_app
from sklearn.neighbors import KDTree

app = Flask(__name__)


class HotelTree:

    tree_keys = ["lon", "lat", "price"]
    return_keys = ["lon", "lat", "name", "stars", "price"]

    def __init__(self, base_df: pd.DataFrame):

        self.coords = np.array(base_df[self.tree_keys])
        self.arr = np.array(base_df[self.return_keys])
        self.tree = KDTree(self.coords, leaf_size=10)

    def query_w_filter(self, input_list):

        input_points = []
        input_filters = []
        for indic in input_list:
            indic["price"] = (indic["min_price"] + indic["max_price"]) / 2
            input_filters.append([-1, -1, indic["max_price"] - indic["price"]])
            input_points.append([indic[k] for k in self.tree_keys])

        dist, _ind = self.tree.query_filtered(
            np.array(input_points), np.array(input_filters)
        )

        ind = [i[0] for i in _ind]

        return [
            {k: a[i] for i, k in enumerate(self.return_keys)}
            if d < np.inf
            else {"missing": True}
            for a, (d,) in zip(self.arr[ind, :], dist)
        ]


@app.route("/started")
def started():
    return "FING"


@app.route("/")
def solution():
    input_json = json.load(open("inputs.json", "r"))
    star_groups = defaultdict(list)
    star_indices = defaultdict(list)
    for i, in_dic in enumerate(input_json):
        sr = in_dic["stars"]
        star_groups[sr].append(in_dic)
        star_indices[sr].append(i)

    out = {}
    for sr, sinp in star_groups.items():
        hotel_tree = current_app.star_dict.get(sr)
        if hotel_tree is None:
            s_out = [{"missing": True} for _ in sinp]
        else:
            s_out = hotel_tree.query_w_filter(sinp)
        for o, ind in zip(s_out, star_indices[sr]):
            out[ind] = o

    out_list = [v for k, v in sorted(out.items(), key=lambda kv: kv[0])]
    json.dump(out_list, open("outputs.json", "w"))
    return "FING"


def shutdown_server():
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()


@app.route("/shutdown")
def shutdown():
    shutdown_server()
    return "Server shutting down..."


app.dfo = (
    pd.read_csv("data.csv")
    .loc[:, ["lon", "lat", "name", "stars", "current-price"]]
    .dropna(how="any")
    .drop_duplicates()
    .assign(
        price=lambda df: df["current-price"]
        .str[1:]
        .str.replace(",", "")
        .astype(float)
    )
)

app.star_dict = {}

for _gid, _gdf in app.dfo.groupby("stars"):
    app.star_dict[_gid] = HotelTree(_gdf)

if __name__ == "__main__":
    app.run(debug=True, port=5112)
