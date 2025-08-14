from __future__ import annotations

import logging
from pathlib import Path
import pandas as pd
from sklearn.metrics import roc_curve, precision_recall_curve, RocCurveDisplay, PrecisionRecallDisplay
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


def plot_curves(y_true, y_prob, plots_dir: Path) -> None:
    plots_dir.mkdir(parents=True, exist_ok=True)
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    RocCurveDisplay(fpr=fpr, tpr=tpr).plot()
    plt.savefig(plots_dir / 'roc_curve.png')
    plt.close()
    prec, rec, _ = precision_recall_curve(y_true, y_prob)
    PrecisionRecallDisplay(precision=prec, recall=rec).plot()
    plt.savefig(plots_dir / 'pr_curve.png')
    plt.close()
    logger.info("Plots saved to %s", plots_dir)

