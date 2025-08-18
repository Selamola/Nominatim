"""Utility helpers for the API."""
from __future__ import annotations

import os
from typing import List, Optional


def get_env_bool(key: str, default: bool = False) -> bool:
    """Read boolean from environment variables."""
    val = os.getenv(key)
    if val is None:
        return default
    return val.lower() in {"1", "true", "yes", "on"}


def dedupe(seq: List[str]) -> List[str]:
    """Remove duplicates while preserving order."""
    seen = set()
    out: List[str] = []
    for item in seq:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out
