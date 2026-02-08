from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from email import policy
from email.message import Message
from email.parser import BytesParser
from email.utils import getaddresses, parsedate_to_datetime
from typing import Protocol

from imapclient import IMAPClient


@dataclass(frozen=True, slots=True)
class EmailRef:
    id: str
    subject: str
    from_address: str
    to_addresses: tuple[str, ...]
    date: datetime
    snippet: str | None = None


@dataclass(frozen=True, slots=True)
class EmailContent:
    id: str
    subject: str
    from_address: str
    to_addresses: tuple[str, ...]
    date: datetime
    text: str | None
    html: str | None
    headers: dict[str, str]


class MailClient(Protocol):
    def list(self, folder: str = "INBOX", limit: int = 100) -> Iterable[EmailRef]: ...

    def get_content(self, email_id: str, folder: str = "INBOX") -> EmailContent: ...

    def move(self, email_id: str, destination: str) -> None: ...


class ImapMailClient:
    """IMAP-backed mail client for listing, fetching, and moving messages."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        *,
        port: int = 993,
        default_folder: str = "INBOX",
    ) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._default_folder = default_folder
        self._client: IMAPClient | None = None

    def __enter__(self) -> ImapMailClient:
        self.connect()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()

    def connect(self) -> None:
        if self._client is not None:
            return
        self._client = IMAPClient(self._host, self._port, ssl=True)
        self._client.login(self._username, self._password)

    def close(self) -> None:
        if self._client is None:
            return
        try:
            self._client.logout()
        finally:
            self._client = None

    def list(self, folder: str = "INBOX", limit: int = 100) -> Iterable[EmailRef]:
        yield from self._list_with_search(["ALL"], folder, limit)

    def list_unseen(self, folder: str = "INBOX", limit: int = 100) -> Iterable[EmailRef]:
        yield from self._list_with_search(["UNSEEN"], folder, limit)

    def get_content(self, email_id: str, folder: str = "INBOX") -> EmailContent:
        client = self._require_connection()
        client.select_folder(folder, readonly=True)
        raw_message = self._fetch_message(int(email_id), client)
        message = _parse_message(raw_message)
        text, html = _extract_text_html(message)
        return EmailContent(
            id=email_id,
            subject=_get_header(message, "subject"),
            from_address=_get_header(message, "from"),
            to_addresses=_parse_addresses(message.get("to")),
            date=_parse_date(message.get("date")),
            text=text,
            html=html,
            headers=_headers_dict(message),
        )

    def move(self, email_id: str, destination: str) -> None:
        client = self._require_connection()
        client.select_folder(self._default_folder, readonly=False)
        client.move([int(email_id)], destination)

    def _require_connection(self) -> IMAPClient:
        if self._client is None:
            raise RuntimeError("IMAP client is not connected.")
        return self._client

    def _list_with_search(
        self,
        criteria: list[str],
        folder: str,
        limit: int,
    ) -> Iterable[EmailRef]:
        client = self._require_connection()
        client.select_folder(folder, readonly=True)
        uids = list(client.search(criteria))
        for uid in uids[-limit:]:
            headers = self._fetch_headers(uid, client)
            yield EmailRef(
                id=str(uid),
                subject=headers["subject"],
                from_address=headers["from_address"],
                to_addresses=headers["to_addresses"],
                date=headers["date"],
            )

    def _fetch_headers(self, uid: int, client: IMAPClient) -> dict[str, object]:
        fetch_data = client.fetch(
            [uid],
            ["BODY.PEEK[HEADER.FIELDS (SUBJECT FROM TO DATE)]"],
        )
        raw = _extract_header_bytes(fetch_data[uid])
        message = _parse_message(raw)
        return {
            "subject": _get_header(message, "subject"),
            "from_address": _get_header(message, "from"),
            "to_addresses": _parse_addresses(message.get("to")),
            "date": _parse_date(message.get("date")),
        }

    def _fetch_message(self, uid: int, client: IMAPClient) -> bytes:
        fetch_data = client.fetch([uid], ["RFC822"])
        raw = fetch_data[uid].get(b"RFC822")
        if not isinstance(raw, (bytes, bytearray)):
            raise RuntimeError("IMAP fetch did not return message bytes.")
        return bytes(raw)


def _extract_header_bytes(fetch_result: dict[bytes, object]) -> bytes:
    for key, value in fetch_result.items():
        if key.startswith(b"BODY[HEADER.FIELDS") and isinstance(value, (bytes, bytearray)):
            return bytes(value)
    raise RuntimeError("IMAP fetch did not return header bytes.")


def _parse_message(raw_message: bytes) -> Message:
    return BytesParser(policy=policy.default).parsebytes(raw_message)


def _parse_addresses(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(addr for _, addr in getaddresses([value]) if addr)


def _parse_date(value: str | None) -> datetime:
    if not value:
        return datetime.fromtimestamp(0, tz=UTC)
    parsed = parsedate_to_datetime(value)
    if parsed is None:
        return datetime.fromtimestamp(0, tz=UTC)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed


def _get_header(message: Message, name: str) -> str:
    return (message.get(name) or "").strip()


def _headers_dict(message: Message) -> dict[str, str]:
    return {key: value for key, value in message.items()}


def _extract_text_html(message: Message) -> tuple[str | None, str | None]:
    text_parts: list[str] = []
    html_parts: list[str] = []

    if message.is_multipart():
        for part in message.walk():
            if part.is_multipart():
                continue
            content_type = part.get_content_type()
            payload = part.get_content()
            if content_type == "text/plain" and isinstance(payload, str):
                text_parts.append(payload)
            if content_type == "text/html" and isinstance(payload, str):
                html_parts.append(payload)
    else:
        payload = message.get_content()
        if isinstance(payload, str):
            text_parts.append(payload)

    text = "\n".join(text_parts).strip() if text_parts else None
    html = "\n".join(html_parts).strip() if html_parts else None
    return text or None, html or None
