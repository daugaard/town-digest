from __future__ import annotations

import json
from datetime import date, time

import pytest

from town_digest.utils import events_extractor


class _FakeResponse:
    def __init__(self, output_text: str) -> None:
        self.output_text = output_text


class _FakeResponsesAPI:
    def __init__(self, output_text: str) -> None:
        self._output_text = output_text

    def create(self, **_: object) -> _FakeResponse:
        return _FakeResponse(self._output_text)


class _FakeOpenAIClient:
    def __init__(self, output_text: str) -> None:
        self.responses = _FakeResponsesAPI(output_text)


def test_extract_events_from_email_text_returns_empty_for_blank_input() -> None:
    drafts = events_extractor.extract_events_from_email_text("   ")

    assert drafts == []


def test_extract_events_from_email_text_normalizes_and_parses_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_text = json.dumps(
        {
            "events": [
                {
                    "title": "  City Budget Meeting  ",
                    "description": "  Review the **2026** draft budget. ",
                    "location": "  City Hall, Room 2 ",
                    "start_date": "2026-03-15",
                    "start_time": "18:30:00",
                },
                {
                    "title": " ",
                    "description": "Ignored because title is blank.",
                    "location": None,
                    "start_date": "2026-03-16",
                    "start_time": None,
                },
            ]
        }
    )
    monkeypatch.setattr(
        events_extractor,
        "build_openai_client",
        lambda: _FakeOpenAIClient(output_text),
    )

    drafts = events_extractor.extract_events_from_email_text("newsletter text")

    assert drafts == [
        {
            "title": "City Budget Meeting",
            "description": "Review the **2026** draft budget.",
            "location": "City Hall, Room 2",
            "start_date": date(2026, 3, 15),
            "start_time": time(18, 30),
        }
    ]


def test_extract_events_from_email_text_raises_for_invalid_start_date(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_text = json.dumps(
        {
            "events": [
                {
                    "title": "Community Cleanup",
                    "description": None,
                    "location": None,
                    "start_date": "March 15, 2026",
                    "start_time": None,
                }
            ]
        }
    )
    monkeypatch.setattr(
        events_extractor,
        "build_openai_client",
        lambda: _FakeOpenAIClient(output_text),
    )

    with pytest.raises(ValueError, match="invalid start_date"):
        events_extractor.extract_events_from_email_text("newsletter text")
