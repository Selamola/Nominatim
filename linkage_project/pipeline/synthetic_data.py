from __future__ import annotations

import logging
from pathlib import Path
from typing import Tuple
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def generate_demo_data(output_dir: Path) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Generate small synthetic df1 and df2 for mock mode."""
    rng = np.random.default_rng(42)
    df1 = pd.DataFrame({
        "REC_CODE": [f"R{i:03d}" for i in range(1, 21)],
        "first_name": rng.choice(["ALICE", "BOB", "CAROL", "DAN"], 20),
        "first_name2": np.nan,
        "last_name": rng.choice(["SMITH", "JONES", "LEE", "KUMAR"], 20),
        "surname2": np.nan,
        "dob": pd.to_datetime("2020-01-01") + pd.to_timedelta(rng.integers(0, 1000, 20), unit="D"),
        "dod": pd.NaT,
        "gender": rng.choice(["M", "F"], 20),
        "hospital_number": rng.integers(1000, 9999, 20).astype(str),
    })
    df2 = pd.DataFrame({
        "report_id": [f"P{i:03d}" for i in range(1, 25)],
        "first_name": rng.choice(["ALICE", "BOB", "CAROL", "DAN"], 24),
        "last_name": rng.choice(["SMITH", "JONES", "LEE", "KUMAR"], 24),
        "report_caretaker_firstname": np.nan,
        "dob": pd.to_datetime("2020-01-01") + pd.to_timedelta(rng.integers(0, 1000, 24), unit="D"),
        "dod": pd.NaT,
        "report_note_dt": pd.NaT,
        "gender": rng.choice(["M", "F"], 24),
        "report_age_class": "NA",
        "report_stillbirth": 0,
        "hospital_number": rng.integers(1000, 9999, 24).astype(str),
        "mom_hospital_number": rng.integers(1000, 9999, 24).astype(str),
    })
    output_dir.mkdir(parents=True, exist_ok=True)
    df1.to_csv(output_dir / "df1.csv", index=False)
    df2.to_csv(output_dir / "df2.csv", index=False)
    logger.info("Synthetic data written to %s", output_dir)
    return df1, df2

