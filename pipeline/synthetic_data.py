from pathlib import Path
import pandas as pd

def generate_demo(output_dir: Path) -> None:
    # Minimal synthetic generator
    output_dir.mkdir(parents=True, exist_ok=True)
    df1 = pd.DataFrame({'REC_CODE': ['R1'], 'first_name': ['ALICE'], 'last_name': ['SMITH']})
    df2 = pd.DataFrame({'report_id': ['T1'], 'first_name': ['ALICE'], 'last_name': ['SMITH']})
    df1.to_csv(output_dir / 'df1.csv', index=False)
    df2.to_csv(output_dir / 'df2.csv', index=False)
