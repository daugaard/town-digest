from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Table

from town_digest.models.base import Base

email_events = Table(
    "email_events",
    Base.metadata,
    Column("email_id", ForeignKey("emails.id"), primary_key=True),
    Column("event_id", ForeignKey("events.id"), primary_key=True),
)

email_announcements = Table(
    "email_announcements",
    Base.metadata,
    Column("email_id", ForeignKey("emails.id"), primary_key=True),
    Column("announcement_id", ForeignKey("announcements.id"), primary_key=True),
)
