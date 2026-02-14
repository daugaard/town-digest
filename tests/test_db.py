from __future__ import annotations

from sqlalchemy import text

from town_digest import db


def test_get_engine_uses_database_url_from_settings(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    db.reset_db_caches()

    engine = db.get_engine()

    assert str(engine.url) == "sqlite+pysqlite:///:memory:"

    engine.dispose()
    db.reset_db_caches()


def test_session_factory_returns_working_session(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    db.reset_db_caches()

    session_factory = db.get_session_factory()
    with session_factory() as session:
        result = session.execute(text("SELECT 1")).scalar_one()

    assert result == 1

    db.get_engine().dispose()
    db.reset_db_caches()
