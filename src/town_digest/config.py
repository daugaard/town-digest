from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_SECRET_KEY = "dev-only-change-me"
DEFAULT_DATABASE_URL = "postgresql://town_digest_user:somepw@localhost/town_digest_dev"
DEFAULT_IMAP_SERVER = "mail.runbox.com"
DEFAULT_IMAP_PORT = 993
DEFAULT_IMAP_USER = "tdigest"


@dataclass(frozen=True, slots=True)
class Settings:
    debug: bool
    secret_key: str
    database_url: str
    imap_server: str
    imap_port: int
    imap_user: str
    imap_password: str = ""  # Optional, can be set via environment variable


def load_settings(app_env: str) -> Settings:
    """Load settings from environment with sane defaults."""
    app_env = app_env.lower() if app_env else os.environ.get("APP_ENV", "development").lower()
    debug = app_env != "production"
    return Settings(
        debug=debug,
        secret_key=os.environ.get("SECRET_KEY", DEFAULT_SECRET_KEY),
        database_url=os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL),
        imap_server=os.environ.get("IMAP_SERVER", DEFAULT_IMAP_SERVER),
        imap_port=int(os.environ.get("IMAP_PORT", DEFAULT_IMAP_PORT)),
        imap_user=os.environ.get("IMAP_USER", DEFAULT_IMAP_USER),
        imap_password=os.environ.get("IMAP_PASSWORD", ""),
    )
