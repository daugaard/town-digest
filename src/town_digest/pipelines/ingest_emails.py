from __future__ import annotations

import prefect

from town_digest.config import load_settings
from town_digest.db import get_session_factory
from town_digest.models.email import Email
from town_digest.pipelines.ingest_email import ingest_email
from town_digest.utils.email_client import EmailContent, ImapMailClient


@prefect.task(name="Fetch Emails")
def fetch_emails() -> list[EmailContent]:
    """Fetch emails from the configured email source."""
    settings = load_settings()
    with ImapMailClient(
        host=settings.imap_server, username=settings.imap_user, password=settings.imap_password
    ) as client:
        emails = []
        for email_ref in client.list_unseen():
            email_content = client.get_content(email_ref.id)
            emails.append(email_content)
    return emails


@prefect.task(name="Persist emails to the database")
def persist_emails(imap_emails: list[EmailContent]) -> list[Email]:
    """Persist IMAP emails to the configured database and return persisted models."""
    if not imap_emails:
        return []

    emails = [
        Email(
            subject=imap_email.subject,
            from_name=imap_email.from_address,
            from_email=imap_email.from_address,
            to_emails=",".join(imap_email.to_addresses),
            message_id=imap_email.id,
            received_at=imap_email.date,
            body_text=imap_email.text,
            body_html=imap_email.html,
        )
        for imap_email in imap_emails
    ]

    session_factory = get_session_factory()
    with session_factory() as session:
        session.add_all(emails)
        session.commit()

    return emails


@prefect.task(name="Mark emails as seen")
def mark_emails_seen(imap_emails: list[EmailContent]) -> None:
    """Mark the given IMAP emails as seen in the email source."""
    settings = load_settings()
    with ImapMailClient(
        host=settings.imap_server, username=settings.imap_user, password=settings.imap_password
    ) as client:
        for email in imap_emails:
            client.mark_seen(email.id)


@prefect.flow(name="Ingest Emails")
def ingest_emails() -> None:
    """Ingest emails from the configured email source."""
    imap_emails = fetch_emails()
    if not imap_emails:
        return

    persisted_emails = persist_emails(imap_emails)
    mark_emails_seen(imap_emails)
    for email in persisted_emails:
        ingest_email(email)


if __name__ == "__main__":
    ingest_emails()
