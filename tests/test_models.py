from __future__ import annotations

from datetime import UTC, date, datetime, time

from sqlalchemy import delete, select

from town_digest.models import (
    Announcement,
    Edition,
    Email,
    EmailAlias,
    EmailStatus,
    Event,
    email_announcements,
    email_events,
)


def test_models_create_tables_and_relationships(db_session) -> None:
    edition = Edition(name="East Windsor", slug="east-windsor", state="NJ")
    alias = EmailAlias(address="tdigest+east-windsor@example.com", edition=edition)
    email = Email(
        edition=edition,
        email_alias=alias,
        subject="Town update",
        received_at=datetime(2025, 1, 1, 12, 0, tzinfo=UTC),
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

    db_session.add(edition)
    db_session.commit()

    persisted_email = db_session.query(Email).one()
    assert persisted_email.events[0].title == "Library Talk"
    assert persisted_email.announcements[0].title == "Budget Update"


def test_deleting_announcement_and_event_cascades_email_assignments(db_session) -> None:
    edition = Edition(name="East Windsor", slug="east-windsor", state="NJ")
    alias = EmailAlias(address="tdigest+east-windsor@example.com", edition=edition)
    email = Email(
        edition=edition,
        email_alias=alias,
        subject="Town update",
        received_at=datetime(2025, 1, 1, 12, 0, tzinfo=UTC),
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

    db_session.add(edition)
    db_session.commit()

    db_session.execute(delete(Announcement).where(Announcement.id == announcement.id))
    db_session.execute(delete(Event).where(Event.id == event.id))
    db_session.commit()

    announcement_links = db_session.execute(select(email_announcements)).all()
    event_links = db_session.execute(select(email_events)).all()
    assert announcement_links == []
    assert event_links == []
