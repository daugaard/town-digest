from __future__ import annotations

from datetime import date, time
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from town_digest.models.associations import email_events
from town_digest.models.base import Base, TimestampedMixin


class Event(TimestampedMixin, Base):
    """A structured event extracted from one or more emails."""

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    edition_id: Mapped[int] = mapped_column(ForeignKey("editions.id"), nullable=False)

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(String(300), nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time | None] = mapped_column(Time, nullable=True)

    edition: Mapped[Edition] = relationship(back_populates="events")
    emails: Mapped[list[Email]] = relationship(
        secondary=email_events,
        back_populates="events",
    )

    def __repr__(self) -> str:
        return f"Event(id={self.id!r}, title={self.title!r})"


if TYPE_CHECKING:
    from town_digest.models.edition import Edition
    from town_digest.models.email import Email
