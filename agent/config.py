from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (lead_agent/)
_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_ROOT / ".env")
load_dotenv()  # also cwd


def _key_from_grok_auth() -> str:
    """Local fallback: use Grok CLI / Grok Build OIDC token if present."""
    auth_path = Path.home() / ".grok" / "auth.json"
    if not auth_path.is_file():
        return ""
    try:
        data = json.loads(auth_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return ""
        for entry in data.values():
            if isinstance(entry, dict):
                key = (entry.get("key") or entry.get("access_token") or "").strip()
                if key:
                    return key
    except (OSError, json.JSONDecodeError, TypeError):
        return ""
    return ""


def resolve_api_key() -> str:
    key = os.getenv("XAI_API_KEY", "").strip()
    if key:
        return key
    return _key_from_grok_auth()


@dataclass(frozen=True)
class Settings:
    api_key: str
    base_url: str = "https://api.x.ai/v1"
    model: str = "grok-4.5"
    default_lead_count: int = 10
    min_score: int = 50

    @classmethod
    def from_env(cls) -> "Settings":
        api_key = resolve_api_key()
        if not api_key:
            raise RuntimeError(
                "Missing XAI_API_KEY.\n"
                "  1) Copy .env.example to .env and add a key from https://console.x.ai\n"
                "  2) Or sign in to Grok CLI so ~/.grok/auth.json exists"
            )
        return cls(
            api_key=api_key,
            base_url=os.getenv("XAI_BASE_URL", "https://api.x.ai/v1").strip(),
            model=os.getenv("XAI_MODEL", "grok-4.5").strip(),
            default_lead_count=int(os.getenv("DEFAULT_LEAD_COUNT", "10")),
            min_score=int(os.getenv("MIN_LEAD_SCORE", "50")),
        )
