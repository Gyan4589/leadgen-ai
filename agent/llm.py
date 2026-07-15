from __future__ import annotations

import json
import re
from typing import Any, Type, TypeVar

from openai import OpenAI
from pydantic import BaseModel

from .config import Settings

T = TypeVar("T", bound=BaseModel)


class LLM:
    """OpenAI-compatible client — works with OpenAI, Groq, Gemini, DeepSeek, OpenRouter, xAI, custom."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = OpenAI(
            api_key=settings.api_key,
            base_url=settings.base_url,
        )

    def complete(
        self,
        system: str,
        user: str,
        *,
        use_web_search: bool = False,
        temperature: float = 0.3,
    ) -> str:
        # use_web_search is handled upstream via agent/search.py for all providers
        _ = use_web_search
        kwargs: dict[str, Any] = {
            "model": self.settings.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
        }
        # Some reasoning models reject temperature
        try:
            response = self.client.chat.completions.create(**kwargs)
        except Exception:
            kwargs.pop("temperature", None)
            response = self.client.chat.completions.create(**kwargs)

        choice = response.choices[0].message
        content = choice.content
        if isinstance(content, str) and content.strip():
            return content.strip()
        return str(content or "").strip()

    def complete_json(
        self,
        system: str,
        user: str,
        schema: Type[T],
        *,
        use_web_search: bool = False,
        temperature: float = 0.2,
    ) -> T:
        schema_hint = json.dumps(schema.model_json_schema(), indent=2)
        full_system = (
            f"{system}\n\n"
            "Return ONLY valid JSON matching this JSON Schema. "
            "No markdown fences, no commentary.\n\n"
            f"{schema_hint}"
        )
        raw = self.complete(
            full_system,
            user,
            use_web_search=use_web_search,
            temperature=temperature,
        )
        data = _parse_json(raw)
        return schema.model_validate(data)


def _parse_json(text: str) -> Any:
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        for pattern in (r"\{[\s\S]*\}", r"\[[\s\S]*\]"):
            match = re.search(pattern, text)
            if match:
                return json.loads(match.group(0))
        raise
