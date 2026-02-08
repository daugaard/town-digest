from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from town_digest.models.base import Base, TimestampedMixin


class EmailAlias(TimestampedMixin, Base):
    """An email alias associated with an edition."""

    __tablename__ = "email_aliases"

    id: Mapped[int] = mapped_column(primary_key=True)
    edition_id: Mapped[int] = mapped_column(ForeignKey("editions.id"), nullable=False)
    address: Mapped[str] = mapped_column(String(320), nullable=False, unique=True, index=True)

    edition: Mapped[Edition] = relationship(back_populates="email_aliases")
    emails: Mapped[list[Email]] = relationship(
        back_populates="email_alias",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"EmailAlias(id={self.id!r}, address={self.address!r})"


if TYPE_CHECKING:
    from town_digest.models.edition import Edition
    from town_digest.models.email import Email
