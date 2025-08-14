from __future__ import annotations

import logging
import pandas as pd
import numpy as np
from pathlib import Path

from .config import load_settings

logger = logging.getLogger(__name__)


def stratified_sample(scored_df: pd.DataFrame, output_dir: Path) -> pd.DataFrame:
    cfg = load_settings()
    sampling = cfg.sampling
    bands = [
        (0.70, 0.80, sampling.get('band_0.70_0.80', 0.40)),
        (0.60, 0.70, sampling.get('band_0.60_0.70', 0.30)),
        (0.50, 0.60, sampling.get('band_0.50_0.60', 0.20)),
        (0.0, 0.50, sampling.get('band_lt_0.50', 0.10)),
    ]
    samples = []
    for low, high, frac in bands:
        mask = (scored_df['final_score'] >= low) & (scored_df['final_score'] < high)
        subset = scored_df[mask]
        if not subset.empty:
            n = max(1, int(len(subset) * frac))
            samples.append(subset.sample(n=n, random_state=42))
    sample_df = pd.concat(samples) if samples else pd.DataFrame()
    output_dir.mkdir(parents=True, exist_ok=True)
    sample_df.to_csv(output_dir / 'sample_for_verification.csv', index=False)
    logger.info("Sample saved to %s", output_dir)
    return sample_df

