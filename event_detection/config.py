"""Configuration kept in one place for the standalone service."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Runtime settings that can later be loaded from environment variables."""

    api_title: str = "EVS Event Detection API"
    default_tolerance_minutes: int = 15
    data_root: str = "zonnedael_data"


settings = Settings()
