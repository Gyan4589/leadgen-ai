"""Popular models users can pick with --model or LEADGEN_MODEL."""

from __future__ import annotations

# name -> (base_url, default_api_key_env, notes)
PROVIDERS: dict[str, dict[str, str]] = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "key_env": "OPENAI_API_KEY",
        "default_model": "gpt-4o",
    },
    "xai": {
        "base_url": "https://api.x.ai/v1",
        "key_env": "XAI_API_KEY",
        "default_model": "grok-3",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "key_env": "GROQ_API_KEY",
        "default_model": "llama-3.3-70b-versatile",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "key_env": "DEEPSEEK_API_KEY",
        "default_model": "deepseek-chat",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "key_env": "OPENROUTER_API_KEY",
        "default_model": "openai/gpt-4o-mini",
    },
    "together": {
        "base_url": "https://api.together.xyz/v1",
        "key_env": "TOGETHER_API_KEY",
        "default_model": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
    },
    "mistral": {
        "base_url": "https://api.mistral.ai/v1",
        "key_env": "MISTRAL_API_KEY",
        "default_model": "mistral-large-latest",
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "key_env": "GEMINI_API_KEY",
        "default_model": "gemini-2.0-flash",
    },
    "custom": {
        "base_url": "",  # set via LEADGEN_BASE_URL
        "key_env": "LEADGEN_API_KEY",
        "default_model": "gpt-4o",
    },
}

# Famous models shortcut → (provider, model_id)
FAMOUS_MODELS: dict[str, tuple[str, str]] = {
    # OpenAI
    "gpt-4o": ("openai", "gpt-4o"),
    "gpt-4o-mini": ("openai", "gpt-4o-mini"),
    "gpt-4.1": ("openai", "gpt-4.1"),
    "gpt-4.1-mini": ("openai", "gpt-4.1-mini"),
    "o3-mini": ("openai", "o3-mini"),
    "o4-mini": ("openai", "o4-mini"),
    # Google
    "gemini-2.0-flash": ("gemini", "gemini-2.0-flash"),
    "gemini-1.5-pro": ("gemini", "gemini-1.5-pro"),
    "gemini-2.5-pro": ("gemini", "gemini-2.5-pro"),
    # Meta via Groq
    "llama-3.3-70b": ("groq", "llama-3.3-70b-versatile"),
    "llama-3.1-70b": ("groq", "llama-3.3-70b-versatile"),
    "mixtral-8x7b": ("groq", "mixtral-8x7b-32768"),
    # DeepSeek
    "deepseek-chat": ("deepseek", "deepseek-chat"),
    "deepseek-v3": ("deepseek", "deepseek-chat"),
    # Mistral
    "mistral-large": ("mistral", "mistral-large-latest"),
    "mistral-small": ("mistral", "mistral-small-latest"),
    # xAI (optional)
    "grok-3": ("xai", "grok-3"),
    "grok-4": ("xai", "grok-4"),
    "grok-4.5": ("xai", "grok-4.5"),
    # OpenRouter popular
    "claude-3.5-sonnet": ("openrouter", "anthropic/claude-3.5-sonnet"),
    "claude-sonnet-4": ("openrouter", "anthropic/claude-sonnet-4"),
    "claude-3-haiku": ("openrouter", "anthropic/claude-3-haiku"),
}


def list_models_help() -> str:
    lines = ["Popular models (use --model NAME):"]
    for name in sorted(FAMOUS_MODELS.keys()):
        provider, mid = FAMOUS_MODELS[name]
        lines.append(f"  {name:22} → {provider:12} {mid}")
    lines.append("")
    lines.append("Providers (use --provider NAME + your API key):")
    for p, meta in PROVIDERS.items():
        lines.append(f"  {p:12} key={meta['key_env']}  default={meta['default_model']}")
    return "\n".join(lines)
