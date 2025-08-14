from __future__ import annotations

import logging
from typing import Tuple
import pandas as pd
import recordlinkage

logger = logging.getLogger(__name__)


def block_records(df1: pd.DataFrame, df2: pd.DataFrame, method: str = "sortedneighborhood", window: int = 15) -> pd.MultiIndex:
    """Return candidate pairs using the chosen blocking method."""
    if method == "exact":
        indexer = recordlinkage.Index()
        indexer.block(left_on="last_name_clean", right_on="last_name_clean")
        indexer.block(left_on="dob_clean", right_on="dob_clean")
        pairs = indexer.index(df1, df2)
    else:
        key_left = df1["gender"] + '_' + df1["last_name_clean"] + '_' + df1["dob_year"].astype(str)
        key_right = df2["gender"] + '_' + df2["last_name_clean"] + '_' + df2["dob_year"].astype(str)
        df1_sorted = df1.assign(block_key=key_left).sort_values("block_key")
        df2_sorted = df2.assign(block_key=key_right).sort_values("block_key")
        indexer = recordlinkage.SortedNeighbourhoodIndex(on="block_key", window=window)
        pairs = indexer.index(df1_sorted, df2_sorted)
    logger.info("Generated %d candidate pairs", len(pairs))
    return pairs

