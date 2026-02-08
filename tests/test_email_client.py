from __future__ import annotations

from town_digest.utils.email_client import _extract_text_html, _parse_addresses, _parse_message


def test_parse_addresses() -> None:
    addresses = _parse_addresses("A <a@example.com>, B <b@example.com>")

    assert addresses == ("a@example.com", "b@example.com")


def test_extract_text_html_prefers_parts() -> None:
    raw = (
        b"From: sender@example.com\r\n"
        b"To: recipient@example.com\r\n"
        b"Subject: Example\r\n"
        b"MIME-Version: 1.0\r\n"
        b'Content-Type: multipart/alternative; boundary="sep"\r\n'
        b"\r\n"
        b"--sep\r\n"
        b"Content-Type: text/plain; charset=utf-8\r\n"
        b"\r\n"
        b"Plain text body.\r\n"
        b"--sep\r\n"
        b"Content-Type: text/html; charset=utf-8\r\n"
        b"\r\n"
        b"<p>HTML body.</p>\r\n"
        b"--sep--\r\n"
    )
    message = _parse_message(raw)
    text, html = _extract_text_html(message)

    assert text == "Plain text body."
    assert html == "<p>HTML body.</p>"
