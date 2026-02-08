from __future__ import annotations

from flask import Flask

from town_digest import config as app_config


def create_app() -> Flask:
    app = Flask(__name__)
    settings = app_config.load_settings()
    app.config.from_mapping(settings.to_dict())

    @app.route("/")
    def hello() -> str:
        return "Hello, Town Digest!"

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])
