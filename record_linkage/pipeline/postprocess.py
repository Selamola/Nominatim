"""Post-processing of prediction results."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd


def deduplicate_and_save(df: pd.DataFrame, out_dir: Path = Path("data/outputs")) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    df = df.sort_values("predicted_prob", ascending=False)
    df = df.drop_duplicates("left_REC_CODE").drop_duplicates("right_report_id")
    df.to_csv(out_dir / f"All_matched_{ts}.csv", index=False)
    df[df["predicted_prob"] >= 0.80].to_csv(out_dir / f"matches_score_ge_0.80_{ts}.csv", index=False)
    df[df["predicted_prob"] >= 0.93].to_csv(out_dir / f"matches_high_conf_ge_0.93_{ts}.csv", index=False)
    summary = df["predicted_match"].value_counts().rename_axis("label").reset_index(name="count")
    summary.to_csv(out_dir / f"summary_{ts}.csv", index=False)
