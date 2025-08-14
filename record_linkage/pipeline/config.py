"""Configuration handling for the pipeline."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from YAML and environment variables."""

    weights: Dict[str, float]
    penalties: Dict[str, float]
    thresholds: Dict[str, float]
    blocking: Dict[str, Any]
    sampling_percents: Dict[str, float]

    sql_server: str | None = None
    sql_database: str | None = None
    sql_username: str | None = None
    sql_password: str | None = None
    redcap_token: str | None = None

    class Config:
        env_file = ".env"
        extra = "ignore"


def load_settings(path: str | Path = Path("configs/settings.yaml")) -> Settings:
    """Load settings from YAML file and environment variables."""
    data = yaml.safe_load(Path(path).read_text())
    return Settings(**data)
