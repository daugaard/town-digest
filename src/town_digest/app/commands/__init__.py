from __future__ import annotations

from flask import Flask

from town_digest.app.commands.seed import register_seed_commands


def register_commands(app: Flask) -> None:
    """Register all CLI command groups for the application."""
    register_seed_commands(app)


__all__ = ["register_commands"]
