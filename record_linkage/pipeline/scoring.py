"""Scoring utilities for candidate pairs."""
from __future__ import annotations

import pandas as pd

from .config import Settings


def apply_scoring(df: pd.DataFrame, settings: Settings) -> pd.DataFrame:
    """Compute final scores and rule-based labels."""
    w = settings.weights
    p = settings.penalties
    df = df.copy()
    df["final_score"] = (
        df["last_name_sim"] * w["last_name_sim"]
        + df["first_name_sim"] * w["first_name_sim"]
        + df["dob_sim"] * w["dob_sim"]
        + df["gender_sim"] * w["gender_sim"]
        + df["hospnum_match"] * w["hospnum_match"]
        + df["is_left_name_missing"] * p["is_left_name_missing"]
        + df["is_right_name_missing"] * p["is_right_name_missing"]
        + df["mom_child_swap_flag"] * p["mom_child_swap_flag"]
    )
    df["final_score_norm"] = (df["final_score"] - df["final_score"].min()) / (
        df["final_score"].max() - df["final_score"].min() + 1e-9
    )
    thresh = settings.thresholds
    df["rule_match"] = (df["final_score"] >= thresh["decision"]).astype(int)
    df["rule_high_conf"] = (df["final_score"] >= thresh["high_confidence"]).astype(int)
    return df
