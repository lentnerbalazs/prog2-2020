import numpy as np
import pandas as pd

lup_cols = [
    "side",
    "match_id",
    "person_id",
    "starter",
    "comes_on",
    "full_bench",
    "sidelined",
    "sub_time",
]

player_cols = [
    "First name",
    "Last name",
    "Nationality",
    "is_lefty",
    "person_id",
]

event_cols = [
    "penalty-miss",
    "yc_all",
    "bookings",
    "sent_off",
    "goal",
    "assist",
    "fh_goal",
]

match_info_cols = [
    "region_id",
    "comp_id",
    "season_id",
    "home_team",
    "away_team",
    "start_time",
    "referee_id",
    "ht_gd",
    "ft_gd",
]


def _filter_error_rounds(_df):
    return ~(
        (_df["season_id"] == _df["round_id"])
        & _df["round_id"].duplicated(keep=False)
    )


def _get_gd(_s):
    return (
        _s.str.extract(r"([0-9]+) - ([0-9]+)")
        .astype(float)
        .pipe(lambda _df: _df[0] - _df[1])
    )


def _parse_time_int(_df):
    return (
        _df["time"]
        .dropna()
        .loc[lambda s: s != "'"]
        .str.replace("'", "")
        .map(eval)
    )


def _is_first_half(_df):
    return (
        _df["time"].str.replace("'", "").str.split("+").str[0].astype(int)
        <= 45
    )


def _fh_goals(_df):
    return (
        _df.loc[lambda df: (df["event"] == "goal") & (df["time"] != "'"), :]
        .loc[_is_first_half, :]
        .assign(event="fh_goal")
    )


class DataRepo:
    def __init__(self):
        self.match_info = pd.DataFrame()
        self.player_x_match = pd.DataFrame()
        self.top5_sideline = pd.DataFrame()
        self.coach_df = pd.DataFrame()
        self.post_red_goals = 0

        self._load_match_details()
        self._load_player_x_match()

    def _load_match_details(self):
        self.match_info = (
            pd.read_hdf("region_df.h5")
            .merge(pd.read_hdf("competition_df.h5"))
            .merge(
                pd.read_hdf("season_df.h5").drop_duplicates(
                    subset=["season_id", "comp_id"]
                )
            )
            .merge(pd.read_hdf("round_df.h5").loc[_filter_error_rounds, :])
            .merge(pd.read_hdf("match_df.h5"))
            .merge(
                pd.read_hdf("match_info_df.h5").assign(
                    ht_gd=lambda df: df["Half-time"].pipe(_get_gd),
                    ft_gd=lambda df: df["Full-time"].pipe(_get_gd),
                )
            )
            .set_index("match_id")
            .loc[:, match_info_cols]
        )

    def _load_player_x_match(self):
        _lup_df = self._get_participant_df()
        _event_raw = pd.read_hdf("event_df.h5")
        self.coach_df = pd.read_hdf("coach_df.h5").assign(
            date=lambda df: self.match_info.reindex(df["match_id"])[
                "start_time"
            ].values
        )

        self._get_goals_after_rc(_event_raw, _lup_df)

        _ids_for_gb = self.match_info.reindex(_lup_df["match_id"]).loc[
            :, ["region_id", "season_id", "referee_id", "start_time"]
        ]

        self.player_x_match = (
            _lup_df.merge(self._get_event_df(_event_raw), how="left")
            .fillna(0)
            .assign(
                sub_time=lambda df: df.loc[:, "sub_time"].replace(0, np.inf),
                sub_goals=lambda df: np.where(df["comes_on"], df["goal"], 0),
                g_a=lambda df: (df["goal"] > 0) & (df["assist"] > 0),
                come_n_go=lambda df: ((df["sent_off"] > 0) & df["comes_on"]),
                region_id=_ids_for_gb["region_id"].values,
                season_id=_ids_for_gb["season_id"].values,
                referee_id=_ids_for_gb["referee_id"].values,
                date=_ids_for_gb["start_time"].values,
            )
        )

    def _get_top5_sideline(self, sideline_df):
        self.top5_sideline = (
            sideline_df.groupby("player_id")
            .agg({"reason": "nunique"})
            .nlargest(5, "reason")
            .reset_index()
            .merge(
                pd.read_hdf("player_df.h5").loc[
                    :, ["player_id", "First name", "Last name", "Nationality"]
                ],
                how="left",
            )
        )

    def _get_goals_after_rc(self, event_raw, lup_raw):
        sided_rel_events = (
            event_raw.loc[
                lambda df: df["event"].isin(["goal", "r-card", "2nd-y-card"])
                & (df["time"] != "'")
            ]
            .merge(
                lup_raw.loc[:, ["match_id", "person_id", "side"]], how="left",
            )
            .assign(
                event=lambda df: df["event"].replace("2nd-y-card", "r-card")
            )
        )
        time_lists = (
            sided_rel_events["time"].str.replace("'", "").str.split("+")
        )

        pr_arr = (
            sided_rel_events.assign(
                main_time=time_lists.str[0].astype(int),
                plus_time=np.where(
                    time_lists.str.len() > 1, time_lists.str[1], "0"
                ).astype(int),
            )
            .sort_values(
                ["match_id", "side", "main_time", "plus_time", "event"]
            )
            .loc[:, ["match_id", "side", "event"]]
            .values
        )

        prg = 0
        pr = False
        for i in range(1, pr_arr.shape[0]):
            if pr_arr[i - 1, 2] == "r-card":
                pr = True
            if (pr_arr[i, 0], pr_arr[i, 1]) != (
                pr_arr[i - 1, 0],
                pr_arr[i - 1, 1],
            ):
                pr = False
            if pr & (pr_arr[i, 2] == "goal"):
                prg += 1

        self.post_red_goals = prg

    @staticmethod
    def _get_event_df(event_raw):

        return (
            pd.concat(
                [
                    event_raw.pipe(lambda df: pd.concat([df, _fh_goals(df)])),
                    pd.read_hdf("goal_df.h5")
                    .dropna(subset=["assister_id"])
                    .assign(
                        event="assist",
                        time=lambda df: df["minute"],
                        person_id=lambda df: df["assister_id"].astype(int),
                    )
                    .loc[:, ["match_id", "person_id", "time", "event"]],
                ]
            )
            .pivot_table(
                columns=["event"],
                index=["match_id", "person_id"],
                values="time",
                aggfunc="count",
            )
            .assign(
                yc=lambda df: (df["y-card"] > 0).astype(int),
                yc2=lambda df: (df["2nd-y-card"] > 0).astype(int),
                rc=lambda df: (df["r-card"] > 0).astype(int),
            )
            .assign(
                bookings=lambda df: df.loc[:, ["yc", "yc2", "rc"]].sum(axis=1),
                sent_off=lambda df: df.loc[:, ["rc", "yc2"]]
                .sum(axis=1)
                .astype(bool)
                .astype(int),
                yc_all=lambda df: df.loc[:, ["yc", "yc2"]].sum(axis=1),
            )
            .loc[:, event_cols]
            .reset_index()
        )

    def _get_participant_df(self):

        _sidelined_raw = pd.read_hdf("sidelined_df.h5")
        self._get_top5_sideline(_sidelined_raw)

        return (
            pd.concat(
                [
                    pd.read_hdf("lineup_df.h5")
                    .assign(
                        starter=True,
                        comes_on=False,
                        full_bench=False,
                        sidelined=False,
                        sub_time=np.inf,
                    )
                    .loc[:, lup_cols],
                    pd.read_hdf("sub_df.h5")
                    .rename(columns={"sub_id": "person_id"})
                    .assign(
                        starter=False,
                        comes_on=lambda df: ~df["subbed_id"].isna(),
                        full_bench=lambda df: df["subbed_id"].isna(),
                        sidelined=False,
                        sub_time=_parse_time_int,
                    )
                    .loc[:, lup_cols],  # note: no need for who was subbed off
                    _sidelined_raw.rename(columns={"player_id": "person_id"})
                    .assign(
                        starter=False,
                        comes_on=False,
                        full_bench=False,
                        sidelined=True,
                        sub_time=np.inf,
                    )
                    .loc[:, lup_cols],
                ]
            )
            .drop_duplicates(
                subset=["person_id", "match_id", "side"], keep="first"
            )
            .merge(
                pd.read_hdf("player_df.h5")
                .rename(columns={"player_id": "person_id"})
                .assign(is_lefty=lambda df: (df["Foot"] == "Left").astype(int))
                .loc[:, player_cols],
                how="left",
            )  # here astype(int) saves a LOT of time
        )
