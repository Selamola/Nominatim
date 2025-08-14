import pandas as pd

from pipeline import cleaning, blocking, features, scoring
from pipeline.synthetic_data import generate_demo
from pipeline.config import load_settings


def test_pipeline_smoke():
    settings = load_settings()
    df1, df2 = generate_demo()
    df1c = cleaning.clean_df(df1, 'left')
    df2c = cleaning.clean_df(df2, 'right')
    pairs = blocking.block(df1c, df2c, method='exact')
    feats = features.compute_features(df1c, df2c, pairs)
    scored = scoring.apply_scoring(feats, settings)
    assert not scored.empty
