from __future__ import annotations

from datetime import date

import markdown
from flask import Flask, abort, render_template
from sqlalchemy import func, select

from town_digest import config as app_config
from town_digest.app.commands import register_commands
from town_digest.db import get_session_factory
from town_digest.models import Announcement, Edition, Event


def create_app() -> Flask:
    app = Flask(__name__)
    settings = app_config.load_settings()
    app.config.from_mapping(settings.to_dict())
    register_commands(app)

    @app.template_filter("markdown")
    def markdown_filter(text: str) -> str:
        return markdown.markdown(text, extensions=["extra", "sane_lists", "nl2br"])

    @app.route("/")
    def hello() -> str:
        session_factory = get_session_factory()
        with session_factory() as session:
            editions = session.scalars(
                select(Edition).order_by(
                    Edition.state.asc(), Edition.name.asc(), Edition.slug.asc()
                )
            ).all()

        return render_template("index.html", editions=editions)

    @app.route("/<state>/<edition_slug>")
    def edition_digest(state: str, edition_slug: str) -> tuple[str, int] | str:
        session_factory = get_session_factory()
        with session_factory() as session:
            edition = session.scalar(
                select(Edition).where(
                    func.lower(Edition.state) == state.lower(),
                    Edition.slug == edition_slug,
                )
            )
            if edition is None:
                abort(404)

            announcements = session.scalars(
                select(Announcement)
                .where(Announcement.edition_id == edition.id)
                .order_by(Announcement.created_at.desc(), Announcement.id.desc())
                .limit(50)
            ).all()

            today = date.today()
            events = session.scalars(
                select(Event)
                .where(
                    Event.edition_id == edition.id,
                    Event.start_date > today,
                )
                .order_by(Event.start_date.asc(), Event.start_time.asc(), Event.id.asc())
                .limit(50)
            ).all()

        return render_template(
            "edition_digest.html",
            edition=edition,
            announcements=announcements,
            events=events,
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])
