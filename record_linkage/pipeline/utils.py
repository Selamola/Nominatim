"""Utility helpers."""
from __future__ import annotations

import logging
from pathlib import Path


def setup_logging() -> None:
    Path("logs").mkdir(exist_ok=True)
    logging.basicConfig(
        filename=Path("logs") / "pipeline.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
