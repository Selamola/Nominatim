from __future__ import annotations

import yaml
from pydantic import BaseSettings, Field
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from YAML and environment."""

    weights: dict = Field(default_factory=dict)
    penalties: dict = Field(default_factory=dict)
    thresholds: dict = Field(default_factory=dict)
    blocking: dict = Field(default_factory=lambda: {"method": "sortedneighborhood", "window": 15})
    sampling: dict = Field(default_factory=dict)

    class Config:
        env_file = Path(__file__).resolve().parents[1] / ".env"


def load_settings() -> Settings:
    """Load settings from configs/settings.yaml and environment."""
    cfg_path = Path(__file__).resolve().parents[1] / "configs" / "settings.yaml"
    data = {}
    if cfg_path.exists():
        with open(cfg_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    return Settings(**data)

