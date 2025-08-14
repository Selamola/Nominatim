"""Generate synthetic demo data."""
from __future__ import annotations

from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd


def generate_demo(out_dir: Path = Path("data/inputs")) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Create small synthetic df1 and df2 datasets for demonstration."""
    rng = np.random.default_rng(42)
    out_dir.mkdir(parents=True, exist_ok=True)

    df1 = pd.DataFrame({
        "REC_CODE": [f"A{i:03d}" for i in range(1, 6)],
        "first_name": ["JOHN", "ANNA", "MIKE", "SARA", "PAUL"],
        "first_name2": [pd.NA] * 5,
        "last_name": ["DOE", "SMITH", "BROWN", "JONES", "LEE"],
        "surname2": [pd.NA] * 5,
        "dob": pd.date_range("2020-01-01", periods=5).tolist(),
        "dod": pd.date_range("2020-06-01", periods=5).tolist(),
        "gender": ["M", "F", "M", "F", "M"],
        "hospital_number": [f"H{i:04d}" for i in range(1, 6)],
        "year": [2020]*5,
        "first_name_original_missing": [False]*5,
        "mom_name": ["ALICE", "BETH", "CAROL", "DIANE", "EVE"],
        "mom_name2": [pd.NA]*5,
    })

    df2 = pd.DataFrame({
        "report_id": [f"R{i:03d}" for i in range(1, 6)],
        "first_name": ["JOHN", "ANNA", "MIKE", "SARA", "PAUL"],
        "last_name": ["DOE", "SMITH", "BROWN", "JONES", "LEE"],
        "report_caretaker_firstname": ["ALICE", "BETH", "CAROL", "DIANE", "EVE"],
        "dob": pd.date_range("2020-01-01", periods=5).tolist(),
        "dod": pd.date_range("2020-06-01", periods=5).tolist(),
        "report_note_dt": pd.date_range("2020-06-02", periods=5).tolist(),
        "gender": ["M", "F", "M", "F", "M"],
        "report_age_class": ["NA"]*5,
        "report_stillbirth": [0]*5,
        "hospital_number": [f"H{i:04d}" for i in range(1, 6)],
        "mom_hospital_number": [f"M{i:04d}" for i in range(1, 6)],
        "child_firstname_original_missing": [False]*5,
        "child_firstname_filled_caretaker": [False]*5,
    })

    df1.to_csv(out_dir / "df1.csv", index=False)
    df2.to_csv(out_dir / "df2.csv", index=False)
    return df1, df2
