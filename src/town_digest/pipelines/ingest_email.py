import prefect
from prefect.logging import get_run_logger

from town_digest.db import get_session_factory
from town_digest.models.announcement import Announcement
from town_digest.models.email import Email
from town_digest.models.email_alias import EmailAlias
from town_digest.models.event import Event
from town_digest.utils.announcement_extractor import extract_announcements_from_email_text


@prefect.task(name="Persists models to the database")
def persist_models(models: list[Announcement | Event]) -> None:
    """Persist parsed announcement and event models."""
    _ = models


@prefect.task(name="Parse Email")
def parse_email(email: Email) -> list[Announcement | Event]:
    """Parse a raw email message into structured models."""
    if email.edition_id is None:
        return []

    email_text = email.body_html or email.body_text or ""
    announcement_drafts = extract_announcements_from_email_text(email_text)
    return [
        Announcement(
            edition_id=email.edition_id,
            title=draft["title"],
            body=draft["body"],
        )
        for draft in announcement_drafts
    ]


@prefect.task(name="Assign email to edition via alias")
def assign_email_to_edition(email: Email, alias: EmailAlias) -> None:
    """Assign the given email to the edition associated with the given alias."""
    session_factory = get_session_factory()
    with session_factory() as session:
        email.edition_id = alias.edition_id
        email.email_alias_id = alias.id
        session.add(email)
        session.commit()


@prefect.task(name="Fetch email alias for email")
def fetch_email_alias(to_addresses: str | None) -> EmailAlias | None:
    """Fetch the email alias id associated with the given recipients."""
    session_factory = get_session_factory()
    with session_factory() as session:
        alias = (
            session.query(EmailAlias)
            .filter(EmailAlias.address.in_(to_addresses.split(",")))
            .one_or_none()
        )
        return alias


@prefect.task(name="Fetch Email from database")
def fetch_email(email_id: int) -> Email:
    """Fetch a single email from the database by ID."""
    session_factory = get_session_factory()
    with session_factory() as session:
        email = session.query(Email).filter(Email.id == email_id).one_or_none()
        if email is None:
            raise ValueError(f"Email with id {email_id} not found.")
        return email


@prefect.flow(name="Ingest Email")
def ingest_email(email_id: int) -> None:
    """Ingest a single email from the configured email source."""
    logger = get_run_logger()
    email = fetch_email(email_id)
    email_alias = fetch_email_alias(email.to_emails)
    if email_alias is None:
        logger.warning(
            "No email alias found for email with id %d and recipients %s", email_id, email.to_emails
        )
        return
    assign_email_to_edition(email, email_alias)
    models = parse_email(email)
    logger.info("Parsed %d models from email with id %d", len(models), email_id)
    persist_models(models)


if __name__ == "__main__":
    ingest_email(8)
