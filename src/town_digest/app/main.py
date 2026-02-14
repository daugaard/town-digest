from __future__ import annotations

from flask import Flask, render_template

from town_digest import config as app_config
from town_digest.app.commands import register_commands


def create_app() -> Flask:
    app = Flask(__name__)
    settings = app_config.load_settings()
    app.config.from_mapping(settings.to_dict())
    register_commands(app)

    @app.route("/")
    def hello() -> str:
        return render_template("index.html")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])
