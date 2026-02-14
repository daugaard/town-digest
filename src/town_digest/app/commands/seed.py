from __future__ import annotations

import click
from flask import Flask

from town_digest.seeds import seed_dev_database


def register_seed_commands(app: Flask) -> None:
    """Register seed-related CLI commands on the Flask app."""

    @app.cli.command("seed-dev")
    def seed_dev_command() -> None:
        """Load baseline development seed data into the configured database."""
        result = seed_dev_database()
        click.echo(
            "Seed complete: "
            f"editions created={result['editions_created']}, "
            f"aliases created={result['aliases_created']}"
        )
