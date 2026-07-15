from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from .models_catalog import FAMOUS_MODELS, PROVIDERS

_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_ROOT / ".env")
load_dotenv()


def _first_env(*names: str) -> str:
    for name in names:
        val = os.getenv(name, "").strip()
        if val:
            return val
    return ""


def resolve_api_key(provider: str) -> str:
    """Accept any common API key env var so users can plug any provider."""
    meta = PROVIDERS.get(provider, PROVIDERS["custom"])
    # provider-specific first, then generic aliases
    return _first_env(
        meta["key_env"],
        "LEADGEN_API_KEY",
        "API_KEY",
        "OPENAI_API_KEY",
        "XAI_API_KEY",
        "GROQ_API_KEY",
        "ANTHROPIC_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "DEEPSEEK_API_KEY",
        "OPENROUTER_API_KEY",
        "TOGETHER_API_KEY",
        "MISTRAL_API_KEY",
    )


@dataclass(frozen=True)
class Settings:
    api_key: str
    base_url: str
    model: str
    provider: str = "openai"
    default_lead_count: int = 10
    min_score: int = 50
    use_web_search: bool = True

    @classmethod
    def from_env(
        cls,
        *,
        provider: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
    ) -> "Settings":
        # CLI / env overrides
        model_name = (model or os.getenv("LEADGEN_MODEL") or os.getenv("MODEL") or "").strip()
        provider_name = (provider or os.getenv("LEADGEN_PROVIDER") or os.getenv("PROVIDER") or "").strip().lower()

        # Resolve famous model shortcuts → provider + model id
        if model_name and model_name.lower() in FAMOUS_MODELS:
            auto_provider, auto_model = FAMOUS_MODELS[model_name.lower()]
            if not provider_name:
                provider_name = auto_provider
            model_name = auto_model

        if not provider_name:
            # Auto-detect from which key is set
            for p, meta in PROVIDERS.items():
                if p == "custom":
                    continue
                if os.getenv(meta["key_env"], "").strip():
                    provider_name = p
                    break
            if not provider_name:
                provider_name = "openai"

        if provider_name not in PROVIDERS:
            provider_name = "custom"

        meta = PROVIDERS[provider_name]
        resolved_base = (
            (base_url or "").strip()
            or os.getenv("LEADGEN_BASE_URL", "").strip()
            or os.getenv("OPENAI_BASE_URL", "").strip()
            or meta["base_url"]
        )
        if not resolved_base:
            resolved_base = "https://api.openai.com/v1"

        if not model_name:
            model_name = (
                os.getenv("LEADGEN_MODEL", "").strip()
                or meta["default_model"]
            )

        key = (api_key or "").strip() or resolve_api_key(provider_name)
        if not key:
            raise RuntimeError(
                "Missing API key. Set any of these in .env or environment:\n"
                "  OPENAI_API_KEY, GROQ_API_KEY, GEMINI_API_KEY, DEEPSEEK_API_KEY,\n"
                "  OPENROUTER_API_KEY, MISTRAL_API_KEY, XAI_API_KEY, LEADGEN_API_KEY, API_KEY\n\n"
                "Examples:\n"
                "  set OPENAI_API_KEY=sk-...\n"
                "  leadgen search \"dental clinics Mumbai\" --model gpt-4o\n"
                "  leadgen search \"gyms Delhi\" --provider groq --model llama-3.3-70b\n"
                "  leadgen models   # list popular models\n"
            )

        web = os.getenv("LEADGEN_WEB_SEARCH", "1").strip().lower() not in {
            "0",
            "false",
            "no",
            "off",
        }

        return cls(
            api_key=key,
            base_url=resolved_base.rstrip("/"),
            model=model_name,
            provider=provider_name,
            default_lead_count=int(os.getenv("DEFAULT_LEAD_COUNT", "10")),
            min_score=int(os.getenv("MIN_LEAD_SCORE", "50")),
            use_web_search=web,
        )
