from __future__ import annotations

import logging
from pathlib import Path
import pandas as pd
import joblib

logger = logging.getLogger(__name__)

FEATURE_COLS = [
    'first_name_sim', 'last_name_sim', 'dob_sim', 'gender_sim', 'hospnum_match',
    'mom_child_swap_flag', 'is_left_name_missing', 'is_right_name_missing'
]


def predict_matches(features: pd.DataFrame, model_dir: Path) -> pd.DataFrame:
    model = joblib.load(model_dir / 'stacked_ensemble_calibrated.pkl')
    threshold = float((model_dir / 'model_threshold.txt').read_text())
    probs = model.predict_proba(features[FEATURE_COLS])[:, 1]
    features['predicted_prob'] = probs
    features['predicted_match'] = (probs >= threshold).astype(int)
    return features

