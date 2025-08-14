# Record Linkage Demo

This project performs end-to-end record linkage with optional Streamlit manual verification.

## Quickstart

```bash
pip install -r requirements.txt
python -m pipeline.cli all --mock
streamlit run apps/manual_verify_app.py
```

See `configs/settings.yaml` for configurable weights and thresholds.
