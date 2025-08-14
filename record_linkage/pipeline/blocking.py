"""Blocking strategies for candidate pair generation."""
from __future__ import annotations

import logging
from typing import Literal

import pandas as pd
import recordlinkage

LOGGER = logging.getLogger(__name__)


def block(df_left: pd.DataFrame, df_right: pd.DataFrame, method: Literal["exact", "sorted"] = "sorted", window: int = 15) -> pd.MultiIndex:
    """Return candidate pairs using the requested blocking method."""
    indexer = recordlinkage.Index()
    if method == "exact":
        indexer.block(left_on=["last_name_clean", "dob_clean"], right_on=["last_name_clean", "dob_clean"])
    else:
        df_left = df_left.copy()
        df_right = df_right.copy()
        df_left["_key"] = df_left["gender"].astype(str) + "_" + df_left["last_name_clean"].astype(str) + "_" + df_left["dob_year"].astype(str)
        df_right["_key"] = df_right["gender"].astype(str) + "_" + df_right["last_name_clean"].astype(str) + "_" + df_right["dob_year"].astype(str)
        indexer.sortedneighbourhood(left_on="_key", right_on="_key", window=window)
    pairs = indexer.index(df_left, df_right)
    LOGGER.info("Generated %s candidate pairs", len(pairs))
    return pairs
