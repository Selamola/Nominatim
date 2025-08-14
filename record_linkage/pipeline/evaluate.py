"""Model evaluation utilities."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from sklearn.calibration import calibration_curve
from sklearn.metrics import precision_recall_curve, roc_curve


def plot_curves(y_true, probas, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    fpr, tpr, _ = roc_curve(y_true, probas)
    prec, rec, _ = precision_recall_curve(y_true, probas)
    frac_pos, mean_pred = calibration_curve(y_true, probas, n_bins=10)

    plt.figure(); plt.plot(fpr, tpr); plt.xlabel('FPR'); plt.ylabel('TPR'); plt.title('ROC Curve'); plt.savefig(out_dir / 'roc.png'); plt.close()
    plt.figure(); plt.plot(rec, prec); plt.xlabel('Recall'); plt.ylabel('Precision'); plt.title('PR Curve'); plt.savefig(out_dir / 'pr.png'); plt.close()
    plt.figure(); plt.plot(mean_pred, frac_pos, marker='o'); plt.xlabel('Mean Predicted'); plt.ylabel('Fraction Positives'); plt.title('Calibration'); plt.savefig(out_dir / 'calibration.png'); plt.close()

    # Cumulative gains curve
    order = np.argsort(-probas)
    cum_pos = np.cumsum(y_true[order]) / y_true.sum()
    perc_samples = np.arange(1, len(y_true)+1) / len(y_true)
    plt.figure(); plt.plot(perc_samples, cum_pos); plt.xlabel('Samples %'); plt.ylabel('Gain'); plt.title('Cumulative Gains'); plt.savefig(out_dir / 'cumulative_gains.png'); plt.close()
