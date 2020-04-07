import pandas as pd
import numpy as np
import functools


def solutions1(a, b, c, d, e, f, g, h, i, j, k, l, m):
    dfs1 = (
        a.merge(b, on="region_id", how="inner")
        .merge(c, on="comp_id", how="inner")
        .merge(d, on="season_id", how="inner")
        .merge(e, on="round_id", how="inner")
        .merge(f, on=["match_id"], how="inner")
    )
    dfs1 = (
        dfs1.groupby(["scorer_id", "region"])
        .agg({"scorer_id": pd.Series.count})
        .reset_index(level=1)
    )
    dfs1 = dfs1[dfs1["scorer_id"] >= 20]
    dfs1 = dfs1.groupby(dfs1.index)["region"].count().reset_index()

    dfs2 = l.merge(g, on=["match_id"], how="inner")
    dfs2 = (
        dfs2[(dfs2["event"] == "2nd-y-card") | (dfs2["event"] == "r-card")]
        .groupby(["referee_id", "person_id"])["person_id"]
        .count()
        .reset_index(drop=True)
    )

    dfs3 = l.merge(f, on=["match_id"], how="inner")
    dfs3 = dfs3[(dfs3["event"] == "2nd-y-card") | (dfs3["event"] == "r-card")]
    dfs3 = dfs3[(dfs3["time"] != "'") & (dfs3["minute"] != "'")]
    dfs3["time"] = (
        dfs3["time"].str[:3].str.replace(r"'", "").str.replace(r"+", "").astype("float")
    )
    dfs3["minute"] = (
        dfs3["minute"]
        .str[:3]
        .str.replace(r"'", "")
        .str.replace(r"+", "")
        .astype("float")
    )

    m.rename(columns={"player_id": "person_id"}, inplace=True)
    dfs4 = m.merge(h, on="person_id", how="inner")
    dfs4 = dfs4[(dfs4.Foot != np.nan) & (dfs4.Foot != "Both")]
    dfs4 = (
        dfs4.groupby(["match_id", "side", "Foot"])["Foot"]
        .count()
        .rename("Feet", inplace=True)
        .reset_index()
    )

    dfs5 = l.merge(k, on="match_id", how="inner")
    dfs5 = dfs5[(dfs5["event"] == "2nd-y-card") | (dfs5["event"] == "r-card")]

    dfs6 = l[(l["event"] == "penalty-miss")]
    dfs6 = dfs6.groupby("match_id")["event"].count().reset_index()

    return (
        len(dfs1[dfs1["region"] == 4]),
        len(dfs2[dfs2 == 2]),
        len(dfs3.query("minute > time")),
        dfs4[dfs4["Foot"] == "Left"].max()[3],
        len(np.where(dfs5["person_id"] == dfs5["sub_id"])[0]),
        len(dfs6[dfs6["event"] >= 2]),
    )
    
def solutions2(a, b, c, d, e, f, g, h, i, j, k, l, m):
    df_top5_assist = (
        c.merge(d, on="season_id")
        .merge(e, on="round_id")
        .merge(f, on="match_id")
        .filter(["season_name", "season_id", "assister_id", "round_id"])
    )
    df_top5_assist.round_id = np.where(df_top5_assist.isna(), 1, 0)
    df_top5_assist = df_top5_assist.rename({"round_id": "assister_num"}, axis=1)
    df_agg = df_top5_assist.groupby(["season_name", "assister_id"])[
        ["assister_num"]
    ].count()
    dfs1 = df_agg["assister_num"].groupby(level=0, group_keys=False).nlargest(5)

    df_top5_subgoals = f.merge(k, on="match_id").filter(["scorer_id", "sub_id"])
    df_top5_subgoals = df_top5_subgoals.loc[
        df_top5_subgoals["scorer_id"] == df_top5_subgoals["sub_id"]
    ]
    df_agg = df_top5_subgoals.groupby(["scorer_id"]).count()
    dfs2 = df_agg.sort_values(by=["sub_id"], ascending=False).head(5)

    df_top5_subs = k[k["time"].isnull()].filter(["sub_id"])
    dfs3 = df_top5_subs["sub_id"].value_counts().head(5)

    return (dfs1, dfs2, dfs3)

def solution3(e):
    df1 = e.copy()
    df1 = df1.reset_index(drop=True).set_index("start_time").sort_index()
    df1["match_start_time"] = df1.index
    df_home = (
        df1.groupby(["home_team", df1.index, "match_id"])["home_team"]
        .count()
        .to_frame()
    )
    df_home.rename(columns={"home_team": "home_played_count"}, inplace=True)
    df_away = (
        df1.groupby(["away_team", df1.index, "match_id"])["away_team"]
        .count()
        .to_frame()
    )
    df_away.rename(columns={"away_team": "away_played_count"}, inplace=True)

    def team1(data_home, data_away, data_all):
        df_ = pd.DataFrame()
        home_teams = data_all.home_team.drop_duplicates().tolist()
        away_teams = data_all.away_team.drop_duplicates().tolist()
        home_team_played = pd.DataFrame()
        away_team_played = pd.DataFrame()
        for hteam, ateam in zip(home_teams, away_teams):
            df_h = data_home.loc[hteam]
            df_h = df_h.reset_index().set_index("start_time").rolling("21D").sum()
            home_team_played = home_team_played.append(df_h)

            df_a = data_away.loc[ateam]
            df_a = df_a.reset_index().set_index("start_time").rolling("21D").sum()
            away_team_played = away_team_played.append(df_a)

        return home_team_played, away_team_played

    played = team1(df_home, df_away, df1)
    home_played = played[0]
    home_played["match_id"] = home_played["match_id"] / home_played["home_played_count"]
    home_played = home_played.drop_duplicates(subset="match_id").reset_index()
    df1 = df1.merge(home_played, on="match_id", how="left")
    df1.home_played_count.fillna(0, inplace=True)
    away_played = played[1]
    away_played["match_id"] = away_played["match_id"] / away_played["away_played_count"]
    away_played = away_played.drop_duplicates(subset="match_id").reset_index()
    df1 = df1.merge(away_played, on="match_id", how="left")
    df1.away_played_count.fillna(0, inplace=True)
    df1.drop(columns=["start_time_x", "start_time_y"], inplace=True)
    return df1
