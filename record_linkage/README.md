# Record Linkage Pipeline

This project provides an end-to-end record linkage pipeline with a Streamlit
interface for manual verification. It supports running in **mock mode** using
synthetic data or **real mode** by extracting data from configured sources.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the full pipeline in mock mode
python -m pipeline.cli all --mock

# Launch the manual verification UI
streamlit run apps/manual_verify_app.py
```

## Configuration

Copy `.env.example` to `.env` and adjust credentials if running in real mode.
Runtime options are controlled via `configs/settings.yaml`.

## Project Structure

See the repository tree for modules and data directories. Intermediate files
are written to `data/temp`, and final outputs to `data/outputs`.

## License

MIT
