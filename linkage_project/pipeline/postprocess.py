from __future__ import annotations

import logging
from pathlib import Path
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)


def postprocess(pred_df: pd.DataFrame, df1: pd.DataFrame, df2: pd.DataFrame, output_dir: Path) -> None:
    ts = datetime.now().strftime('%Y%m%d_%H%M')
    merged = pred_df.merge(df1, left_on='df1_index', right_index=True, suffixes=('_feat', '_left'))
    merged = merged.merge(df2, left_on='df2_index', right_index=True, suffixes=('', '_right'))
    merged = merged.sort_values('predicted_prob', ascending=False)
    merged = merged.drop_duplicates('REC_CODE').drop_duplicates('report_id')
    output_dir.mkdir(parents=True, exist_ok=True)
    merged.to_csv(output_dir / f'All_matched_{ts}.csv', index=False)
    merged[merged['predicted_prob'] >= 0.80].to_csv(output_dir / f'matches_score_ge_0.80_{ts}.csv', index=False)
    merged[merged['predicted_prob'] >= 0.93].to_csv(output_dir / f'matches_high_conf_ge_0.93_{ts}.csv', index=False)
    logger.info("Postprocess outputs written to %s", output_dir)

