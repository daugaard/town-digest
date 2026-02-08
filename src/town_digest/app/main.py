from __future__ import annotations

from flask import Flask

from town_digest import config as app_config


def create_app() -> Flask:
    app = Flask(__name__)
    settings = app_config.load_settings()
    app.config.from_mapping(
        DEBUG=settings.debug,
        SECRET_KEY=settings.secret_key,
        DATABASE_URL=settings.database_url,
    )

    @app.route("/")
    def hello() -> str:
        return "Hello, Town Digest!"

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])
