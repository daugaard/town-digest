from __future__ import annotations

import json
import os
from datetime import date, time
from typing import Any, TypedDict

from town_digest.utils.openai_client import build_openai_client

DEFAULT_OPENAI_MODEL = "gpt-5-mini"


class EventDraft(TypedDict):
    title: str
    description: str | None
    location: str | None
    start_date: date
    start_time: time | None


EVENTS_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "events": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": ["string", "null"]},
                    "location": {"type": ["string", "null"]},
                    "start_date": {"type": "string"},
                    "start_time": {"type": ["string", "null"]},
                },
                "required": ["title", "description", "location", "start_date", "start_time"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["events"],
    "additionalProperties": False,
}


def extract_events_from_email_text(
    email_text: str,
    *,
    model: str | None = None,
) -> list[EventDraft]:
    """Extract structured civic events from email text using OpenAI structured output."""
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
                    "Extract civic events from newsletter text. "
                    "Only return events with a clear title and explicit calendar date. "
                    "DO NOT return non-event announcements, subscribe calls, or generic newsletter text. "
                    "The description MUST be markdown-formatted, the title MUST be plain text. "
                    "Return start_date as YYYY-MM-DD and start_time as 24-hour HH:MM:SS when known; "
                    "otherwise set start_time to null. "
                    "Include location when explicitly present; otherwise set location to null. "
                    "If there are no events, return an empty list."
                ),
            },
            {"role": "user", "content": email_text},
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "event_extraction",
                "schema": EVENTS_JSON_SCHEMA,
                "strict": True,
            }
        },
    )

    output_text = response.output_text
    if not output_text:
        raise ValueError("OpenAI did not return structured output text for event extraction.")

    parsed = json.loads(output_text)
    events = parsed.get("events")
    if not isinstance(events, list):
        raise ValueError("OpenAI response schema violation: 'events' must be a list.")

    drafts: list[EventDraft] = []
    for item in events:
        title = item.get("title")
        if not isinstance(title, str) or not title.strip():
            continue

        start_date = _parse_start_date(item.get("start_date"))
        start_time = _parse_start_time(item.get("start_time"))
        description = _normalize_optional_text(item.get("description"))
        location = _normalize_optional_text(item.get("location"))

        drafts.append(
            {
                "title": title.strip(),
                "description": description,
                "location": location,
                "start_date": start_date,
                "start_time": start_time,
            }
        )

    return drafts


def _normalize_optional_text(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized if normalized else None


def _parse_start_date(value: object) -> date:
    if not isinstance(value, str):
        raise ValueError("OpenAI response schema violation: 'start_date' must be a string.")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(
            f"OpenAI response schema violation: invalid start_date {value!r}."
        ) from exc


def _parse_start_time(value: object) -> time | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("OpenAI response schema violation: 'start_time' must be a string or null.")
    try:
        return time.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(
            f"OpenAI response schema violation: invalid start_time {value!r}."
        ) from exc
