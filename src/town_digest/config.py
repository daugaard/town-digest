from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_SECRET_KEY = "dev-only-change-me"
DEFAULT_DATABASE_URL = "postgresql+psycopg://town_digest_user:somepw@localhost/town_digest_dev"
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

    def to_dict(self) -> dict[str, str | bool | int]:
        """Convert settings to a dictionary for easy use in Flask config."""
        return {
            "DEBUG": self.debug,
            "SECRET_KEY": self.secret_key,
            "DATABASE_URL": self.database_url,
            "IMAP_SERVER": self.imap_server,
            "IMAP_PORT": self.imap_port,
            "IMAP_USER": self.imap_user,
            "IMAP_PASSWORD": self.imap_password,
        }


def load_settings() -> Settings:
    """Load settings from environment with sane defaults."""
    debug_raw = os.environ.get("DEBUG", "")
    debug = debug_raw.strip().lower() in {"1", "true", "yes", "on"} if debug_raw else True
    return Settings(
        debug=debug,
        secret_key=os.environ.get("SECRET_KEY", DEFAULT_SECRET_KEY),
        database_url=os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL),
        imap_server=os.environ.get("IMAP_SERVER", DEFAULT_IMAP_SERVER),
        imap_port=int(os.environ.get("IMAP_PORT", DEFAULT_IMAP_PORT)),
        imap_user=os.environ.get("IMAP_USER", DEFAULT_IMAP_USER),
        imap_password=os.environ.get("IMAP_PASSWORD", ""),
    )
