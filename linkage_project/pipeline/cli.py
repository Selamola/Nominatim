from __future__ import annotations

import logging
from pathlib import Path
import typer
import pandas as pd

from . import io_sources, cleaning, blocking, features, scoring, sampling, train, predict, postprocess, utils
from .config import load_settings

app = typer.Typer()

DATA_DIR = Path(__file__).resolve().parents[1] / 'data'
TEMP_DIR = DATA_DIR / 'temp'
OUTPUTS_DIR = DATA_DIR / 'outputs'
MODELS_DIR = Path(__file__).resolve().parents[1] / 'models'
LOGS_DIR = Path(__file__).resolve().parents[1] / 'logs'


@app.command()
def extract(mock: bool = True):
    utils.setup_logging(LOGS_DIR)
    df1, df2 = io_sources.extract_data(mock=mock)
    df1.to_parquet(TEMP_DIR / 'df1_raw.parquet')
    df2.to_parquet(TEMP_DIR / 'df2_raw.parquet')


@app.command()
def clean():
    utils.setup_logging(LOGS_DIR)
    df1 = pd.read_parquet(TEMP_DIR / 'df1_raw.parquet')
    df2 = pd.read_parquet(TEMP_DIR / 'df2_raw.parquet')
    df1_c, df2_c = cleaning.clean_data(df1, df2)
    df1_c.to_parquet(TEMP_DIR / 'df1_clean.parquet')
    df2_c.to_parquet(TEMP_DIR / 'df2_clean.parquet')


@app.command()
def block():
    utils.setup_logging(LOGS_DIR)
    cfg = load_settings()
    df1 = pd.read_parquet(TEMP_DIR / 'df1_clean.parquet')
    df2 = pd.read_parquet(TEMP_DIR / 'df2_clean.parquet')
    pairs = blocking.block_records(df1, df2, cfg.blocking.get('method'), cfg.blocking.get('window', 15))
    pd.DataFrame(index=pairs).to_parquet(TEMP_DIR / 'pairs.parquet')


@app.command()
def features_cmd():
    utils.setup_logging(LOGS_DIR)
    df1 = pd.read_parquet(TEMP_DIR / 'df1_clean.parquet')
    df2 = pd.read_parquet(TEMP_DIR / 'df2_clean.parquet')
    pairs = pd.read_parquet(TEMP_DIR / 'pairs.parquet').index
    feat_df = features.compute_features(df1, df2, pairs)
    feat_df.to_parquet(TEMP_DIR / 'features.parquet')


@app.command()
def score():
    utils.setup_logging(LOGS_DIR)
    feat_df = pd.read_parquet(TEMP_DIR / 'features.parquet')
    scored = scoring.score_features(feat_df)
    scored.to_parquet(TEMP_DIR / 'scored.parquet')


@app.command()
def sample():
    utils.setup_logging(LOGS_DIR)
    scored = pd.read_parquet(TEMP_DIR / 'scored.parquet')
    sampling.stratified_sample(scored, OUTPUTS_DIR)


@app.command()
def train_cmd():
    utils.setup_logging(LOGS_DIR)
    features_df = pd.read_parquet(TEMP_DIR / 'scored.parquet')
    labels_path = OUTPUTS_DIR / 'verified_matches.csv'
    if not labels_path.exists():
        typer.echo('No verified_matches.csv found.')
        raise typer.Exit()
    labels = pd.read_csv(labels_path)
    train.train_models(features_df, labels, MODELS_DIR, OUTPUTS_DIR / 'plots')


@app.command()
def predict_cmd():
    utils.setup_logging(LOGS_DIR)
    features_df = pd.read_parquet(TEMP_DIR / 'scored.parquet')
    pred = predict.predict_matches(features_df, MODELS_DIR)
    pred.to_parquet(TEMP_DIR / 'predictions.parquet')


@app.command()
def postprocess_cmd():
    utils.setup_logging(LOGS_DIR)
    pred = pd.read_parquet(TEMP_DIR / 'predictions.parquet')
    df1 = pd.read_parquet(TEMP_DIR / 'df1_clean.parquet')
    df2 = pd.read_parquet(TEMP_DIR / 'df2_clean.parquet')
    postprocess.postprocess(pred, df1, df2, OUTPUTS_DIR)


@app.command()
def all(mock: bool = True):
    extract(mock=mock)
    clean()
    block()
    features_cmd()
    score()
    sample()
    typer.echo("Pipeline completed. Use train/predict/postprocess separately when labels available.")


if __name__ == "__main__":
    app()

