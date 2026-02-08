from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from town_digest.models.base import Base, TimestampedMixin


class Edition(TimestampedMixin, Base):
    """A geographic edition that groups emails, events, and announcements."""

    __tablename__ = "editions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    state: Mapped[str] = mapped_column(String(2), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    email_aliases: Mapped[list[EmailAlias]] = relationship(
        back_populates="edition",
        cascade="all, delete-orphan",
    )
    emails: Mapped[list[Email]] = relationship(
        back_populates="edition",
        cascade="all, delete-orphan",
    )
    events: Mapped[list[Event]] = relationship(
        back_populates="edition",
        cascade="all, delete-orphan",
    )
    announcements: Mapped[list[Announcement]] = relationship(
        back_populates="edition",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Edition(id={self.id!r}, slug={self.slug!r}, state={self.state!r})"


if TYPE_CHECKING:
    from town_digest.models.announcement import Announcement
    from town_digest.models.email import Email
    from town_digest.models.email_alias import EmailAlias
    from town_digest.models.event import Event
