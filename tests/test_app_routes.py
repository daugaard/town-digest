from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from town_digest.app import main as main_module
from town_digest.app.main import create_app
from town_digest.models import Announcement, Base, Edition, EmailAlias, Event


def test_edition_digest_route_renders_limited_announcements_and_future_events(monkeypatch) -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection: object, _: object) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    with Session(engine) as session:
        edition = Edition(name="East Windsor", slug="east-windsor", state="NJ")
        alias = EmailAlias(address="tdigest+east-windsor@example.com", edition=edition)
        session.add_all([edition, alias])

        announcements = [
            Announcement(edition=edition, title=f"Announcement {idx}", body=f"Body {idx}")
            for idx in range(55)
        ]
        session.add_all(announcements)

        future_events = [
            Event(
                edition=edition,
                title=f"Future Event {idx}",
                description=f"Future event description {idx}",
                start_date=date.today() + timedelta(days=idx + 1),
            )
            for idx in range(55)
        ]
        past_event = Event(
            edition=edition,
            title="Past Event",
            description="This should not render.",
            start_date=date.today() - timedelta(days=1),
        )
        session.add_all([*future_events, past_event])
        session.commit()

    monkeypatch.setattr(main_module, "get_session_factory", lambda: session_factory)

    app = create_app()
    app.config.update(TESTING=True)
    client = app.test_client()

    response = client.get("/nj/east-windsor")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "East Windsor" in body
    assert body.count('class="announcement-item') == 50
    assert body.count('class="event-item') == 50
    assert "Past Event" not in body
    assert "Future Event 0" in body
