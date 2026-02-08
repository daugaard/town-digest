from __future__ import annotations

from datetime import date, datetime, time, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from town_digest.models import (
    Announcement,
    Base,
    Edition,
    Email,
    EmailAlias,
    EmailStatus,
    Event,
)


def test_models_create_tables_and_relationships() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    edition = Edition(name="East Windsor", slug="east-windsor", state="NJ")
    alias = EmailAlias(address="tdigest+east-windsor@example.com", edition=edition)
    email = Email(
        edition=edition,
        email_alias=alias,
        subject="Town update",
        received_at=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
        status=EmailStatus.RECEIVED,
        body_text="Hello",
    )
    event = Event(
        edition=edition,
        title="Library Talk",
        start_date=date(2025, 2, 1),
        start_time=time(18, 30),
    )
    announcement = Announcement(
        edition=edition,
        title="Budget Update",
        body="Details forthcoming",
    )

    email.events.append(event)
    email.announcements.append(announcement)

    with Session(engine) as session:
        session.add(edition)
        session.commit()

        persisted_email = session.query(Email).one()
        assert persisted_email.events[0].title == "Library Talk"
        assert persisted_email.announcements[0].title == "Budget Update"
