from __future__ import annotations

import os

from openai import OpenAI


def build_openai_client() -> OpenAI:
    """Build an OpenAI client from environment configuration."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is required.")
    return OpenAI(api_key=api_key)
