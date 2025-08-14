from __future__ import annotations

import logging
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from sklearn.calibration import CalibratedClassifierCV
from imblearn.over_sampling import SMOTE
import joblib

logger = logging.getLogger(__name__)

FEATURE_COLS = [
    'first_name_sim', 'last_name_sim', 'dob_sim', 'gender_sim', 'hospnum_match',
    'mom_child_swap_flag', 'is_left_name_missing', 'is_right_name_missing'
]


def train_models(features: pd.DataFrame, labels: pd.DataFrame, model_dir: Path, plots_dir: Path) -> float:
    df = features.merge(labels, on=['df1_index', 'df2_index'])
    df = df[df['label'].isin([0, 1])]
    X = df[FEATURE_COLS]
    y = df['label']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    smote = SMOTE(random_state=42)
    X_train_res, y_train_res = smote.fit_resample(X_train, y_train)

    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    mlp = MLPClassifier(hidden_layer_sizes=(50,), max_iter=500, random_state=42)
    estimators = [('rf', rf), ('mlp', mlp)]
    stack = StackingClassifier(estimators=estimators, final_estimator=LogisticRegression(max_iter=1000))
    stack.fit(X_train_res, y_train_res)
    calibrated = CalibratedClassifierCV(stack, method='sigmoid', cv=5)
    calibrated.fit(X_train_res, y_train_res)

    probas = calibrated.predict_proba(X_test)[:, 1]
    best_th, best_f1 = 0.5, 0
    for th in np.linspace(0, 1, 101):
        preds = (probas >= th).astype(int)
        score = f1_score(y_test, preds)
        if score > best_f1:
            best_f1, best_th = score, th
    model_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(calibrated, model_dir / 'stacked_ensemble_calibrated.pkl')
    (model_dir / 'model_threshold.txt').write_text(f"{best_th:.2f}")
    logger.info("Model trained with best threshold %.2f", best_th)
    return best_th

