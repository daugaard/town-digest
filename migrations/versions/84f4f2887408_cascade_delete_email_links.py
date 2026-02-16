"""Cascade delete email link rows

Revision ID: 84f4f2887408
Revises: 6a2efc896fbd
Create Date: 2026-02-16 15:10:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "84f4f2887408"
down_revision: str | Sequence[str] | None = "6a2efc896fbd"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(
        "email_announcements_email_id_fkey",
        "email_announcements",
        type_="foreignkey",
    )
    op.drop_constraint(
        "email_announcements_announcement_id_fkey",
        "email_announcements",
        type_="foreignkey",
    )
    op.drop_constraint(
        "email_events_email_id_fkey",
        "email_events",
        type_="foreignkey",
    )
    op.drop_constraint(
        "email_events_event_id_fkey",
        "email_events",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "email_announcements_email_id_fkey",
        "email_announcements",
        "emails",
        ["email_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "email_announcements_announcement_id_fkey",
        "email_announcements",
        "announcements",
        ["announcement_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "email_events_email_id_fkey",
        "email_events",
        "emails",
        ["email_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "email_events_event_id_fkey",
        "email_events",
        "events",
        ["event_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "email_announcements_email_id_fkey",
        "email_announcements",
        type_="foreignkey",
    )
    op.drop_constraint(
        "email_announcements_announcement_id_fkey",
        "email_announcements",
        type_="foreignkey",
    )
    op.drop_constraint(
        "email_events_email_id_fkey",
        "email_events",
        type_="foreignkey",
    )
    op.drop_constraint(
        "email_events_event_id_fkey",
        "email_events",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "email_announcements_email_id_fkey",
        "email_announcements",
        "emails",
        ["email_id"],
        ["id"],
    )
    op.create_foreign_key(
        "email_announcements_announcement_id_fkey",
        "email_announcements",
        "announcements",
        ["announcement_id"],
        ["id"],
    )
    op.create_foreign_key(
        "email_events_email_id_fkey",
        "email_events",
        "emails",
        ["email_id"],
        ["id"],
    )
    op.create_foreign_key(
        "email_events_event_id_fkey",
        "email_events",
        "events",
        ["event_id"],
        ["id"],
    )
