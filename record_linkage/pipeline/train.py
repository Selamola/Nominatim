"""Model training for record linkage."""
from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.inspection import permutation_importance

from .config import Settings
from . import evaluate

FEATURE_COLS = [
    "first_name_sim",
    "last_name_sim",
    "dob_sim",
    "gender_sim",
    "hospnum_match",
    "mom_child_swap_flag",
    "is_left_name_missing",
    "is_right_name_missing",
]


def train_models(df: pd.DataFrame, settings: Settings, model_dir: Path = Path("models"), plot_dir: Path = Path("data/outputs/plots")) -> float:
    model_dir.mkdir(parents=True, exist_ok=True)
    plot_dir.mkdir(parents=True, exist_ok=True)

    X = df[FEATURE_COLS]
    y = df["label"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, stratify=y, random_state=42)

    smote = SMOTE(random_state=42)
    X_res, y_res = smote.fit_resample(X_train, y_train)

    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    mlp = MLPClassifier(hidden_layer_sizes=(50,), max_iter=200, random_state=42)
    estimators = [("rf", rf), ("mlp", mlp)]
    stack = StackingClassifier(estimators=estimators, final_estimator=LogisticRegression(max_iter=1000, random_state=42))
    clf = CalibratedClassifierCV(stack, method="sigmoid")
    clf.fit(X_res, y_res)

    probas = clf.predict_proba(X_test)[:, 1]
    evaluate.plot_curves(y_test.values, probas, plot_dir)

    thresholds = np.arange(0.0, 1.01, 0.01)
    f1_scores = [f1_score(y_test, probas >= t) for t in thresholds]
    best_thresh = float(thresholds[int(np.argmax(f1_scores))])

    joblib.dump(clf, model_dir / "stacked_ensemble_calibrated.pkl")
    (model_dir / "model_threshold.txt").write_text(str(best_thresh))

    # Model comparison table
    models = {"RandomForest": rf, "MLP": mlp, "Stacked": stack}
    comparison = []
    for name, model in models.items():
        model.fit(X_res, y_res)
        auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
        comparison.append({"model": name, "roc_auc": auc})
    pd.DataFrame(comparison).to_csv(plot_dir / "model_comparison.csv", index=False)

    perm = permutation_importance(clf, X_test, y_test, random_state=42)
    imp_df = pd.DataFrame({"feature": FEATURE_COLS, "importance": perm.importances_mean})
    imp_df.to_csv(plot_dir / "permutation_importance.csv", index=False)
    return best_thresh
