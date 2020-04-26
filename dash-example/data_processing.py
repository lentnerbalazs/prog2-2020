import itertools
import json
import os

import numpy as np
import pandas as pd
import requests

match_url = "https://borza-hotelcom-data.s3.eu-central-1.amazonaws.com/whoscored-match-1376867.json"
match_fp = "match.json"

if os.path.exists(match_fp):
    match_dic = json.load(open(match_fp))
else:
    match_dic = json.loads(requests.get(match_url).content)
    json.dump(match_dic, open(match_fp, "w"))

rel_stat_names = [
    "shotsOnTarget",
    "shotsOffTarget",
    "interceptions",
    "possession",
    "passesTotal",
    "passesAccurate",
    "passesKey",
]


team_id_dic = {
    match_dic[v]["teamId"]: f"{v} - {match_dic[v]['name']}" for v in ["home", "away"]
}

touches = [
    {
        "team": team_id_dic[e["teamId"]],
        "x": e["x"],
        "y": e["y"],
        "type": e["type"]["displayName"],
    }
    for e in match_dic["events"]
    if e.get("isTouch")
]

team_stats = [
    {"stat": rs, "team": side, "value": sum(match_dic[side]["stats"][rs].values())}
    for rs in rel_stat_names
    for side in ["home", "away"]
]

players = [
    {
        "name": p["name"],
        "position": p["position"],
        "age": p["age"],
        "height": p["height"],
        "weight": p["weight"],
        "side": side,
    }
    for side in ["home", "away"]
    for p in match_dic[side]["players"]
    if p.get("isFirstEleven")
]

pos_classes = {
    "defender": ["DC", "DR", "DL"],
    "forward": ["FW", "ST", "RW", "LW"],
    "goalkeeper": ["GK"],
}
default_pos = "midfielder"

pos_class_df = pd.DataFrame(
    [
        {"position": p, "position_class": pc}
        for pc, pl in pos_classes.items()
        for p in pl
    ]
)


match_title = (
    f'{match_dic["home"]["name"]} {match_dic["score"]} {match_dic["away"]["name"]}'
)
player_df = pd.DataFrame(players).merge(pos_class_df, how="left").fillna(default_pos)
touch_df = pd.DataFrame(touches)
stat_df = pd.DataFrame(team_stats)
