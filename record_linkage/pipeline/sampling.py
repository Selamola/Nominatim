"""Sampling and rule-based labeling."""
from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from .config import Settings

LOGGER = logging.getLogger(__name__)


def create_verification_sample(df: pd.DataFrame, settings: Settings, out_path: Path = Path("data/outputs/sample_for_verification.csv")) -> pd.DataFrame:
    """Create stratified sample for manual verification."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    remaining = df[df["rule_match"] == 0]
    percents = settings.sampling_percents

    bands = [
        (0.70, 0.80, percents["band_70_80"]),
        (0.60, 0.70, percents["band_60_70"]),
        (0.50, 0.60, percents["band_50_60"]),
        (0.00, 0.50, percents["band_0_50"]),
    ]
    samples = []
    for low, high, frac in bands:
        band_df = remaining[(remaining["final_score"] >= low) & (remaining["final_score"] < high)]
        if not band_df.empty:
            samples.append(band_df.sample(frac=frac, random_state=42))
    sample_df = pd.concat(samples, ignore_index=True) if samples else pd.DataFrame()
    sample_df.to_csv(out_path, index=False)
    LOGGER.info("Saved verification sample to %s", out_path)
    return sample_df
