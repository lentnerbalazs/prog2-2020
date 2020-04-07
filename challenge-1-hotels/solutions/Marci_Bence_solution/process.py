import pandas as pd
import numpy as np
import json
import pickle

input_locations = json.load(open('inputs.json', 'r'))
df = pd.read_pickle("accommodations")

with open('Ball_Tree', 'rb') as f:
    bt = pickle.load(f)

query_lats = []
query_lons = []

input_locations = json.load(open('inputs.json', 'r'))
for elements in input_locations:
    query_lats.append(elements["lat"])
    query_lons.append(elements["lon"])


distances, indices = bt.query(np.c_[query_lats, query_lons])

nearest_cities = df.iloc[[item for sublist in indices.tolist() for item in sublist],]
answers = [{'lat': x['lat'],'lon':x['lon'],'name':x['name']} for index, x in nearest_cities.iterrows()]

json.dump(answers,open('outputs.json','w'))