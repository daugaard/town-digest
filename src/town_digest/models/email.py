from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from town_digest.models.announcement import Announcement
from town_digest.models.associations import email_announcements, email_events
from town_digest.models.base import Base, TimestampedMixin
from town_digest.models.edition import Edition
from town_digest.models.email_alias import EmailAlias
from town_digest.models.event import Event


class EmailStatus(StrEnum):
    RECEIVED = "received"
    PROCESSED = "processed"


class Email(TimestampedMixin, Base):
    """A received email associated with an edition and alias."""

    __tablename__ = "emails"

    id: Mapped[int] = mapped_column(primary_key=True)
    edition_id: Mapped[int] = mapped_column(ForeignKey("editions.id"), nullable=False)
    email_alias_id: Mapped[int] = mapped_column(ForeignKey("email_aliases.id"), nullable=False)

    subject: Mapped[str | None] = mapped_column(String(500), nullable=True)
    from_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    from_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    message_id: Mapped[str | None] = mapped_column(String(500), nullable=True, unique=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    body_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_html: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[EmailStatus] = mapped_column(
        SAEnum(EmailStatus, name="email_status", native_enum=False),
        nullable=False,
        default=EmailStatus.RECEIVED,
        server_default=EmailStatus.RECEIVED.value,
    )

    edition: Mapped[Edition] = relationship(back_populates="emails")
    email_alias: Mapped[EmailAlias] = relationship(back_populates="emails")
    events: Mapped[list[Event]] = relationship(
        secondary=email_events,
        back_populates="emails",
    )
    announcements: Mapped[list[Announcement]] = relationship(
        secondary=email_announcements,
        back_populates="emails",
    )

    def __repr__(self) -> str:
        return f"Email(id={self.id!r}, subject={self.subject!r})"
