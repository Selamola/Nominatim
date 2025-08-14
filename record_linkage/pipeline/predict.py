"""Predict matches using trained model."""
from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

from .train import FEATURE_COLS


def predict_matches(df: pd.DataFrame, model_dir: Path = Path("models")) -> pd.DataFrame:
    model = joblib.load(model_dir / "stacked_ensemble_calibrated.pkl")
    threshold = float((model_dir / "model_threshold.txt").read_text())
    prob = model.predict_proba(df[FEATURE_COLS])[:, 1]
    df = df.copy()
    df["predicted_prob"] = prob
    df["predicted_match"] = (prob >= threshold).astype(int)
    df["match_source"] = "model"
    return df
