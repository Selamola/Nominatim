from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Dict
from pathlib import Path
import yaml

class Settings(BaseSettings):
    """Global configuration loaded from YAML and environment variables."""
    mock: bool = True
    weights: Dict[str, float] = {
        "last_name_sim": 0.40,
        "first_name_sim": 0.30,
        "dob_sim": 0.20,
        "gender_sim": 0.05,
        "hospnum_match": 0.05,
    }
    penalties: Dict[str, float] = {
        "is_left_name_missing": -0.03,
        "is_right_name_missing": -0.03,
        "mom_child_swap_flag": 0.02,
    }
    thresholds: Dict[str, float] = {
        "decision": 0.80,
        "high_confidence": 0.93,
    }
    blocking_method: int = 2
    blocking_window: int = 15
    sampling: Dict[str, float] = {
        "0.70_0.80": 0.40,
        "0.60_0.70": 0.30,
        "0.50_0.60": 0.20,
        "0.00_0.50": 0.10,
    }

    model_config = SettingsConfigDict(env_file=".env")


def load_settings(path: Path = Path("configs/settings.yaml")) -> Settings:
    """Load settings merging YAML and environment variables."""
    data = {}
    if path.exists():
        with open(path, "r", encoding="utf8") as f:
            data = yaml.safe_load(f) or {}
    return Settings(**data)
