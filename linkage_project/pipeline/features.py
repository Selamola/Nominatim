from __future__ import annotations

import logging
from typing import Tuple

import pandas as pd
import numpy as np
import textdistance

logger = logging.getLogger(__name__)


def _jw(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return textdistance.jaro_winkler.normalized_similarity(a, b)


def _dob_sim(a: pd.Timestamp, b: pd.Timestamp) -> float:
    if pd.isna(a) or pd.isna(b):
        return 0.0
    diff = abs((a - b).days)
    if diff == 0:
        return 1.0
    if diff <= 3:
        return 0.8
    if diff <= 30:
        return 0.5
    return 0.0


def compute_features(df1: pd.DataFrame, df2: pd.DataFrame, pairs: pd.MultiIndex) -> pd.DataFrame:
    """Compute similarity features for candidate pairs."""
    pairs_df = pd.DataFrame(index=pairs)
    pairs_df['first_name_sim'] = pairs_df.index.map(lambda idx: _jw(df1.loc[idx[0], 'first_name_clean'], df2.loc[idx[1], 'first_name_clean']))
    pairs_df['last_name_sim'] = pairs_df.index.map(lambda idx: _jw(df1.loc[idx[0], 'last_name_clean'], df2.loc[idx[1], 'last_name_clean']))
    pairs_df['dob_sim'] = pairs_df.index.map(lambda idx: _dob_sim(df1.loc[idx[0], 'dob_clean'], df2.loc[idx[1], 'dob_clean']))
    pairs_df['gender_sim'] = pairs_df.index.map(lambda idx: float(df1.loc[idx[0], 'gender'] == df2.loc[idx[1], 'gender']))
    pairs_df['hospnum_match'] = pairs_df.index.map(lambda idx: float(
        df1.loc[idx[0], 'hospital_number'] in {df2.loc[idx[1], 'hospital_number'], df2.loc[idx[1], 'mom_hospital_number']}
    ))
    pairs_df['mom_child_swap_flag'] = pairs_df.index.map(lambda idx: float(
        'hospital_number_mom' in df1.columns and df1.loc[idx[0], 'hospital_number_mom'] == df2.loc[idx[1], 'hospital_number']
    ))
    pairs_df['is_left_name_missing'] = pairs_df.index.map(lambda idx: float(df1.loc[idx[0], 'first_name_clean'] == ''))
    pairs_df['is_right_name_missing'] = pairs_df.index.map(lambda idx: float(df2.loc[idx[1], 'first_name_clean'] == ''))
    pairs_df = pairs_df.reset_index().rename(columns={'level_0': 'df1_index', 'level_1': 'df2_index'})
    return pairs_df

