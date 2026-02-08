from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_SECRET_KEY = "dev-only-change-me"
DEFAULT_DATABASE_URL = "postgresql://localhost/town_digest"


@dataclass(frozen=True, slots=True)
class Settings:
    debug: bool
    secret_key: str
    database_url: str


def load_settings(app_env: str) -> Settings:
    """Load settings from environment with sane defaults."""
    app_env = app_env.lower() if app_env else os.environ.get("APP_ENV", "development").lower()
    debug = app_env != "production"
    return Settings(
        debug=debug,
        secret_key=os.environ.get("SECRET_KEY", DEFAULT_SECRET_KEY),
        database_url=os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL),
    )
