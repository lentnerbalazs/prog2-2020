import pickle
import pandas as pd
import numpy as np
import json

input_dicts = json.load(open("inputs.json", "r"))

star_dict = pickle.load(open("sd.pkl", "rb"))

min_distances = [np.inf] * len(input_dicts)

answers = [{"missing": True}] * len(input_dicts)

for input_idx, input_dict in enumerate(input_dicts):

    star_arr = star_dict.get(input_dict["stars"])
    if star_arr is None:
        continue

    max_price = input_dict["max_price"]
    min_price = input_dict["min_price"]

    i_max = np.searchsorted(star_arr[:, 4], max_price)
    i_min = np.searchsorted(star_arr[:, 4], min_price)

    if i_max <= i_min:
        continue

    filtered_arr = star_arr[i_min:i_max, :]

    input_p = np.array([input_dict["lon"], input_dict["lat"]])
    distances = ((filtered_arr[:, (0, 1)] - input_p) ** 2).sum(axis=1)
    closest_i = np.argmin(distances)

    ans = filtered_arr[closest_i, :]
    answers[input_idx] = {k: v for v, k in zip(ans, ["lon", "lat", "name", "stars", "price"])}


json.dump(answers, open("outputs.json", "w"))
