from __future__ import annotations

import json
import os
from typing import Any, TypedDict

from town_digest.utils.openai_client import build_openai_client

DEFAULT_OPENAI_MODEL = "gpt-5-mini"


class AnnouncementDraft(TypedDict):
    title: str | None
    body: str


ANNOUNCEMENTS_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "announcements": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": ["string", "null"]},
                    "body": {"type": "string"},
                },
                "required": ["title", "body"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["announcements"],
    "additionalProperties": False,
}


def extract_announcements_from_email_text(
    email_text: str,
    *,
    model: str | None = None,
) -> list[AnnouncementDraft]:
    """Extract civic announcements from email text using OpenAI structured output."""
    if not email_text.strip():
        return []

    selected_model = model or os.environ.get("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
    llm_client = build_openai_client()

    response = llm_client.responses.create(
        model=selected_model,
        input=[
            {
                "role": "system",
                "content": (
                    "Extract non-event civic announcements from newsletter text. "
                    "DO NOT return newsletter sign-up calls, welcome announcements, event listings, or other non-announcement content. "
                    "Return concise reworded announcements that are suitable for display on a website."
                    "The body MUST be markdown-formatted, the title MUST be plain text."
                    "Feel free to include links in the body if there are any relevant links in the email text. "
                    "If there are no announcements, return an empty list."
                ),
            },
            {"role": "user", "content": email_text},
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "announcement_extraction",
                "schema": ANNOUNCEMENTS_JSON_SCHEMA,
                "strict": True,
            }
        },
    )

    output_text = response.output_text
    if not output_text:
        raise ValueError(
            "OpenAI did not return structured output text for announcement extraction."
        )

    parsed = json.loads(output_text)
    announcements = parsed.get("announcements")
    if not isinstance(announcements, list):
        raise ValueError("OpenAI response schema violation: 'announcements' must be a list.")

    drafts: list[AnnouncementDraft] = []
    for item in announcements:
        title = item.get("title")
        body = item.get("body")
        normalized_body = body.strip()
        if not normalized_body:
            continue

        normalized_title = title.strip() if isinstance(title, str) and title.strip() else None
        drafts.append({"title": normalized_title, "body": normalized_body})

    return drafts
