"""REDCap integration (simplified)."""
from __future__ import annotations

import os
import logging
from typing import List

import httpx
from sqlmodel import Session

from .seed import seed_mock_data
from .utils import get_env_bool

logger = logging.getLogger(__name__)


def sync_redcap(session: Session) -> int:
    """Fetch data from REDCap or seed mock data.

    Returns number of records inserted.
    """
    tokens = [t.strip() for t in os.getenv("REDCAP_TOKENS", "").split(",") if t.strip()]
    enabled = get_env_bool("REDCAP_ENABLED", False)
    if not enabled or not tokens:
        seed_mock_data(session)
        return 0
    # Simplified: real implementation would call REDCap API.
    # We avoid external calls in this demo; just log and return.
    logger.info("REDCap sync requested but not implemented in demo environment")
    return 0
