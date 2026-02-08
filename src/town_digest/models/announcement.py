from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from town_digest.models.associations import email_announcements
from town_digest.models.base import Base, TimestampedMixin

if TYPE_CHECKING:
    from town_digest.models.edition import Edition
    from town_digest.models.email import Email


class Announcement(TimestampedMixin, Base):
    """An unstructured announcement extracted from one or more emails."""

    __tablename__ = "announcements"

    id: Mapped[int] = mapped_column(primary_key=True)
    edition_id: Mapped[int] = mapped_column(ForeignKey("editions.id"), nullable=False)

    title: Mapped[str | None] = mapped_column(String(300), nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    edition: Mapped[Edition] = relationship(back_populates="announcements")
    emails: Mapped[list[Email]] = relationship(
        secondary=email_announcements,
        back_populates="announcements",
    )

    def __repr__(self) -> str:
        return f"Announcement(id={self.id!r}, title={self.title!r})"
