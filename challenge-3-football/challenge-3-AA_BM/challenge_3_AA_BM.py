import pandas as pd


def key_df(match_df, round_df, season_df, competition_df):
    key_df = match_df[["round_id", "match_id"]]
    key_df = pd.merge(key_df, round_df)[["match_id", "round_id", "season_id"]]
    key_df = pd.merge(key_df, season_df)[
        ["match_id", "round_id", "season_id", "comp_id"]
    ]
    key_df = pd.merge(key_df, competition_df)[
        ["match_id", "round_id", "season_id", "comp_id", "region_id"]
    ]
    return key_df


def name_df(player_df):
    player_df["name"] = player_df["First name"] + " " + player_df["Last name"]
    player_df_merge = player_df[["player_id", "name"]]
    return player_df_merge


def elso_feladat(goal_df, key_df):

    goal_df_tmp = goal_df.rename(columns={"scorer_id": "player_id"})
    key_df = key_df.merge(goal_df_tmp[["player_id", "match_id"]])

    scorers_above_twenty = (
        goal_df_tmp.player_id.value_counts()
        .reset_index(name="occurences")
        .query("occurences > 20")["index"]
    )
    bool_masker = key_df["player_id"].isin(scorers_above_twenty)
    x = (
        key_df[bool_masker]
        .groupby("player_id")
        .nunique()
        .apply(lambda x: True if x["region_id"] == 4 else False, axis=1)
    )
    return len(x[x == True].index)


def masodik_feladat(event_df, match_info_df):

    tmp_df = event_df.merge(match_info_df[["match_id", "referee_id"]])

    x = (
        tmp_df[(tmp_df.event.isin(["r-card", "2nd-y-card"]))]
        .groupby("referee_id")
        .nunique()
        .apply(lambda x: True if x["person_id"] == 2 else False, axis=1)
    )
    return len(x[x == True].index)


def negyedik_feladat(player_df, lineup_df):
    player_df_tmp = player_df[player_df["Foot"] == "Left"]
    tmp_df = lineup_df.rename(columns={"person_id": "player_id"}).merge(
        player_df_tmp[["player_id"]]
    )
    x = tmp_df.groupby(["match_id", "side"]).nunique().max().player_id

    return x


def otodik_feladat(event_df, sub_df):

    x = len(
        event_df[(event_df.event.isin(["r-card", "2nd-y-card"]))]
        .merge(sub_df.dropna().rename(columns={"sub_id": "person_id"})["person_id"])
        .drop_duplicates()
    )
    return x


def hatodik_feladat(event_df):
    y = (
        event_df[event_df["event"] == "penalty-miss"]
        .groupby("match_id")
        .nunique()
        .apply(lambda x: True if x["time"] > 2 else False, axis=1)
    )
    x = print(len(y[y == True].index))
    return x


def top5_assister(goal_df, key_df, player_df_merge):
    key_df_top50 = goal_df.merge(key_df[["match_id", "season_id"]], how="left")
    assister_top = pd.DataFrame(
        key_df_top50.groupby(["season_id", "assister_id"])
        .size()
        .rename("count")
        .reset_index()
    )
    assister_top = assister_top.groupby("season_id").apply(
        lambda x: x.nlargest(5, "count", keep="all")
    )
    assister_top["assister_id"] = assister_top["assister_id"].astype("int64")
    assister_top = (
        assister_top.rename(columns={"assister_id": "player_id"})
        .merge(player_df_merge)
        .sort_values("season_id")
    )
    return assister_top[["name", "season_id", "count"]]


def topsub_goal(sub_df, goal_df, player_df_merge):
    sub_df_top = sub_df.rename(columns={"sub_id": "player_id"}).loc[
        sub_df["subbed_id"].notnull()
    ]
    sub_df_top["player_id"] = sub_df_top["player_id"].astype("Float32").astype("Int32")
    goal_df["player_id"] = goal_df.rename(
        columns={"scorer_id": "player_id"}
    ).player_id.astype("Int32")
    sub_top = goal_df[["match_id", "player_id"]].merge(
        sub_df_top[["player_id", "match_id", "time"]],
        how="left",
        on=["player_id", "match_id"],
    )
    sub_top = (
        pd.DataFrame(sub_top.loc[sub_top["time"].notnull()])
        .groupby(["match_id", "player_id"])
        .size()
        .rename("count")
        .reset_index()
    )
    sub_top = pd.DataFrame(sub_top[["player_id", "count"]]).sort_values(
        "count", ascending=False
    )[0:5]
    sub_top = sub_top.merge(player_df_merge)
    return sub_top


def top_bench(sub_df, player_df_merge):
    bench_top = sub_df.rename(columns={"sub_id": "player_id"}).loc[
        sub_df["subbed_id"].isnull()
    ]
    bench_top = bench_top.player_id.value_counts()
    bench_top = pd.DataFrame(bench_top)
    bench_top = bench_top.rename(columns={"player_id": "bench_count"}).sort_values(
        "bench_count", ascending=False
    )[0:5]
    bench_top = bench_top.merge(player_df_merge, left_index=True, right_on="player_id")
    return bench_top


def top_half(goal_df, player_df_merge):
    goal_df1 = goal_df.copy()
    goal_df1["minute"] = goal_df1["minute"].str.rsplit("'")
    a = pd.DataFrame(goal_df1.minute.tolist(), columns=["half", "other"])
    a = pd.DataFrame(a["half"])
    goal_df1 = goal_df1.merge(a, left_index=True, right_index=True)
    half_top = goal_df1.sort_values("half").reset_index(drop=True)
    half_top = half_top[1:]
    half_top["half"] = half_top["half"].astype(int)
    half_top = half_top.loc[half_top["half"] <= 45]
    half_top = pd.DataFrame(
        half_top.groupby("player_id").size().rename("count").reset_index()
    )
    half_top = half_top.sort_values("count", ascending=False)[0:5]
    half_top = half_top.merge(player_df_merge, on="player_id")
    return half_top


def top_sideline(sidelined_df, player_df_merge):
    diff_side_df = sidelined_df
    diff_side_df = (
        pd.DataFrame(diff_side_df.groupby("player_id").reason.nunique())
        .sort_values("reason", ascending=False)
        .nlargest(5, "reason", keep="all")
    )
    diff_side_df = diff_side_df.merge(
        player_df_merge, left_index=True, right_on="player_id"
    )
    return diff_side_df


def feature1(match_df):
    match_re = match_df.rename(
        columns={"home_team": "away_team", "away_team": "home_team"}
    )
    match_concat_df = pd.concat([match_df, match_re], sort=True)
    match_concat_df = match_concat_df[["home_team", "start_time", "match_id"]]
    feature_final_df = match_df[["match_id", "home_team", "away_team", "start_time"]]

    feature = match_concat_df[["home_team", "start_time"]].sort_values("start_time")
    feature["home_counter"] = 1
    counter1 = pd.DataFrame(
        feature.groupby("home_team").apply(
            lambda x: x.set_index("start_time").rolling("21D").home_counter.count()
        )
    ).reset_index(level=[0, 1])

    feature = feature[["home_team", "start_time"]].merge(
        counter1, on=["home_team", "start_time"]
    )
    feature["home_counter"] = feature["home_counter"] - 1

    feature1 = feature_final_df.merge(
        feature, on=["home_team", "start_time"], how="left"
    )
    feature1 = feature1.merge(
        feature.rename(
            columns={"home_counter": "away_counter", "home_team": "away_team"}
        ),
        on=["away_team", "start_time"],
        how="left",
    ).sort_values("home_team")

    return feature1