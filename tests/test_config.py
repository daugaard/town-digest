from __future__ import annotations

from town_digest import config as app_config
from town_digest.app.main import create_app


def test_default_config_uses_development(monkeypatch) -> None:
    monkeypatch.delenv("DEBUG", raising=False)
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)

    app = create_app()

    assert app.config["DEBUG"] is True
    assert app.config["SECRET_KEY"] == app_config.DEFAULT_SECRET_KEY
    assert app.config["DATABASE_URL"] == app_config.DEFAULT_DATABASE_URL


def test_env_overrides_production_config(monkeypatch) -> None:
    monkeypatch.setenv("DEBUG", "0")
    monkeypatch.setenv("SECRET_KEY", "super-secret")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/town_digest")

    app = create_app()

    assert app.config["DEBUG"] is False
    assert app.config["SECRET_KEY"] == "super-secret"
    assert app.config["DATABASE_URL"] == "postgresql://user:pass@localhost/town_digest"


def test_load_settings_defaults_to_development() -> None:
    settings = app_config.load_settings()

    assert settings.debug is True
