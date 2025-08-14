"""Command line interface for the record linkage pipeline."""
from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
import typer

from . import blocking, cleaning, features, io_sources, predict, sampling, scoring, train, postprocess
from .config import load_settings
from .utils import setup_logging

app = typer.Typer()


@app.command()
def extract(mock: bool = False) -> None:
    setup_logging()
    settings = load_settings()
    io_sources.load_inputs(mock, settings)


@app.command()
def clean() -> None:
    setup_logging()
    settings = load_settings()
    df1, df2 = io_sources.load_inputs(False, settings)
    df1 = cleaning.clean_df(df1, "left")
    df2 = cleaning.clean_df(df2, "right")
    Path("data/temp").mkdir(parents=True, exist_ok=True)
    df1.to_parquet("data/temp/df1_clean.parquet")
    df2.to_parquet("data/temp/df2_clean.parquet")


@app.command()
def block_data() -> None:
    setup_logging()
    settings = load_settings()
    df1 = pd.read_parquet("data/temp/df1_clean.parquet")
    df2 = pd.read_parquet("data/temp/df2_clean.parquet")
    pairs = blocking.block(df1, df2, settings.blocking["method"], settings.blocking["window"])
    pd.DataFrame(list(pairs), columns=["df1_index", "df2_index"]).to_parquet("data/temp/pairs.parquet", index=False)


@app.command()
def features_step() -> None:
    setup_logging()
    df1 = pd.read_parquet("data/temp/df1_clean.parquet")
    df2 = pd.read_parquet("data/temp/df2_clean.parquet")
    pairs = pd.read_parquet("data/temp/pairs.parquet")
    pairs_idx = pd.MultiIndex.from_frame(pairs)
    feats = features.compute_features(df1, df2, pairs_idx)
    feats.to_parquet("data/temp/features.parquet", index=False)


@app.command()
def score() -> None:
    setup_logging()
    settings = load_settings()
    df = pd.read_parquet("data/temp/features.parquet")
    df = scoring.apply_scoring(df, settings)
    df.to_parquet("data/temp/scored.parquet", index=False)


@app.command()
def sample() -> None:
    setup_logging()
    settings = load_settings()
    df = pd.read_parquet("data/temp/scored.parquet")
    sampling.create_verification_sample(df, settings)


@app.command()
def train_model() -> None:
    setup_logging()
    settings = load_settings()
    df = pd.read_parquet("data/temp/scored.parquet")
    labels_path = Path("data/outputs/verified_matches.csv")
    if labels_path.exists():
        labels = pd.read_csv(labels_path)
        df = df.merge(labels, on=["df1_index", "df2_index"], how="inner")
        train.train_models(df, settings)
    else:
        logging.warning("Verified matches not found. Skipping training.")


@app.command()
def predict_step() -> None:
    setup_logging()
    df = pd.read_parquet("data/temp/scored.parquet")
    df = predict.predict_matches(df)
    df.to_parquet("data/temp/predictions.parquet", index=False)


@app.command()
def postprocess_step() -> None:
    setup_logging()
    df = pd.read_parquet("data/temp/predictions.parquet")
    postprocess.deduplicate_and_save(df)


@app.command()
def all(mock: bool = typer.Option(False, help="Use synthetic data")) -> None:
    extract(mock)
    clean()
    block_data()
    features_step()
    score()
    sample()
    # Training and prediction require manual labels; run if available
    if Path("data/outputs/verified_matches.csv").exists():
        train_model()
        predict_step()
        postprocess_step()


if __name__ == "__main__":
    app()
