from __future__ import annotations

import logging
import pandas as pd

from .config import load_settings

logger = logging.getLogger(__name__)


def score_features(feat_df: pd.DataFrame) -> pd.DataFrame:
    """Compute weighted final_score and normalized score."""
    cfg = load_settings()
    weights = cfg.weights
    penalties = cfg.penalties
    feat_df['final_score'] = (
        feat_df['last_name_sim'] * weights.get('last_name_sim', 0)
        + feat_df['first_name_sim'] * weights.get('first_name_sim', 0)
        + feat_df['dob_sim'] * weights.get('dob_sim', 0)
        + feat_df['gender_sim'] * weights.get('gender_sim', 0)
        + feat_df['hospnum_match'] * weights.get('hospnum_match', 0)
        + feat_df['is_left_name_missing'] * penalties.get('is_left_name_missing', 0)
        + feat_df['is_right_name_missing'] * penalties.get('is_right_name_missing', 0)
        + feat_df['mom_child_swap_flag'] * penalties.get('mom_child_swap_flag', 0)
    )
    # normalize
    min_s, max_s = feat_df['final_score'].min(), feat_df['final_score'].max()
    feat_df['final_score_norm'] = (feat_df['final_score'] - min_s) / (max_s - min_s + 1e-9)
    thresholds = cfg.thresholds
    feat_df['rule_match'] = feat_df['final_score'] >= thresholds.get('decision', 0.8)
    feat_df['rule_high_conf'] = feat_df['final_score'] >= thresholds.get('high_confidence', 0.93)
    return feat_df

