"""Feature engineering for record linkage."""
from __future__ import annotations

import logging
from typing import Tuple

import numpy as np
import pandas as pd
import textdistance

LOGGER = logging.getLogger(__name__)


def _dob_similarity(a: pd.Series, b: pd.Series) -> pd.Series:
    diff = (a - b).abs().dt.days
    sim = pd.Series(0.0, index=a.index)
    sim = sim.where(a.isna() | b.isna(), np.select([
        diff == 0,
        diff <= 3,
        diff <= 30,
    ], [1.0, 0.8, 0.5], default=0.0))
    return sim


def compute_features(df_left: pd.DataFrame, df_right: pd.DataFrame, pairs: pd.MultiIndex) -> pd.DataFrame:
    """Compute similarity features for candidate pairs."""
    pairs_df = pd.DataFrame(list(pairs), columns=["df1_index", "df2_index"])
    left = df_left.loc[pairs_df["df1_index"]].reset_index().add_prefix("left_")
    right = df_right.loc[pairs_df["df2_index"]].reset_index().add_prefix("right_")
    df = pd.concat([pairs_df, left, right], axis=1)

    df["first_name_sim"] = df.apply(
        lambda x: textdistance.jaro_winkler(x["left_first_name_clean"], x["right_first_name_clean"]), axis=1
    )
    df["last_name_sim"] = df.apply(
        lambda x: textdistance.jaro_winkler(x["left_last_name_clean"], x["right_last_name_clean"]), axis=1
    )
    df["dob_sim"] = _dob_similarity(df["left_dob_clean"], df["right_dob_clean"])
    df["gender_sim"] = (df["left_gender"] == df["right_gender"]).astype(float)
    df["hospnum_match"] = (
        (df["left_hospital_number"] == df["right_hospital_number"]) |
        (df["left_hospital_number"] == df.get("right_mom_hospital_number", ""))
    ).astype(float)
    df["mom_child_swap_flag"] = (
        df.get("left_hospital_number_mom", pd.Series(""))
        == df.get("right_hospital_number", pd.Series(""))
    ).astype(float)
    df["is_left_name_missing"] = df["left_is_name_missing"].astype(float)
    df["is_right_name_missing"] = df["right_is_name_missing"].astype(float)
    return df
