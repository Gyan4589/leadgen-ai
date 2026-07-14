from __future__ import annotations

import json
import re
from typing import Any, Optional, Type, TypeVar

from openai import OpenAI
from pydantic import BaseModel

from .config import Settings

T = TypeVar("T", bound=BaseModel)


class LLM:
    """Thin wrapper around the xAI Responses API (OpenAI-compatible)."""

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
        tools: Optional[list[dict[str, Any]]] = None
        if use_web_search:
            tools = [{"type": "web_search"}]

        kwargs: dict[str, Any] = {
            "model": self.settings.model,
            "input": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
        }
        if tools:
            kwargs["tools"] = tools

        response = self.client.responses.create(**kwargs)
        text = getattr(response, "output_text", None)
        if text:
            return text.strip()
        return _extract_output_text(response).strip()

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


def _extract_output_text(response: Any) -> str:
    """Fallback parser if output_text is missing on the SDK object."""
    chunks: list[str] = []
    for item in getattr(response, "output", None) or []:
        for part in getattr(item, "content", None) or []:
            text = getattr(part, "text", None)
            if text:
                chunks.append(text)
            elif isinstance(part, dict) and part.get("text"):
                chunks.append(part["text"])
    if chunks:
        return "\n".join(chunks)
    return str(response)


def _parse_json(text: str) -> Any:
    text = text.strip()
    # Strip markdown fences if the model still adds them
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Best-effort: first {...} or [...]
        for pattern in (r"\{[\s\S]*\}", r"\[[\s\S]*\]"):
            match = re.search(pattern, text)
            if match:
                return json.loads(match.group(0))
        raise
