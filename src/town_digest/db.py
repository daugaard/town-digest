from __future__ import annotations

from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from town_digest.config import load_settings


@lru_cache(maxsize=1)
def get_engine(database_url: str | None = None) -> Engine:
    """Create and cache the SQLAlchemy engine for the configured database."""
    resolved_database_url = database_url or load_settings().database_url
    connect_args: dict[str, bool] = {}
    if resolved_database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    return create_engine(
        resolved_database_url,
        connect_args=connect_args,
        pool_pre_ping=True,
    )


@lru_cache(maxsize=1)
def get_session_factory(database_url: str | None = None) -> sessionmaker[Session]:
    """Return a cached session factory bound to the configured engine."""
    return sessionmaker(
        bind=get_engine(database_url),
        autoflush=False,
        expire_on_commit=False,
    )


def reset_db_caches() -> None:
    """Clear DB engine/session caches for tests and process reconfiguration."""
    get_session_factory.cache_clear()
    get_engine.cache_clear()
