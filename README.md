# LeadGen AI

**Search any keywords → get real sales leads**

**Works with any AI API** — OpenAI, Groq, Gemini, DeepSeek, OpenRouter, Mistral, Together, custom OpenAI-compatible servers, and more.

**Developed by Gyan Ranjan**

---

## Install

```bash
pip install leadgen-ai
```

From GitHub:

```bash
pip install git+https://github.com/Gyan4589/leadgen-ai.git
```

---

## Setup (any API key)

Create a `.env` or set an environment variable. **Use the key for the provider you choose:**

```bash
# OpenAI
set OPENAI_API_KEY=sk-...

# or Groq (fast + free tier)
set GROQ_API_KEY=gsk_...

# or Google Gemini
set GEMINI_API_KEY=...

# or DeepSeek / OpenRouter / Mistral
set DEEPSEEK_API_KEY=...
set OPENROUTER_API_KEY=...
set MISTRAL_API_KEY=...

# or generic
set LEADGEN_API_KEY=...
set LEADGEN_BASE_URL=https://api.openai.com/v1
set LEADGEN_MODEL=gpt-4o
```

---

## Usage

```bash
# list popular models
leadgen models

# search keywords
leadgen search "dental clinics Mumbai" -n 8

# pick a famous model
leadgen search "real estate agents Texas" -m gpt-4o -n 5
leadgen search "AI startups Bangalore" -m gemini-2.0-flash
leadgen search "gyms Delhi" -p groq -m llama-3.3-70b
leadgen search "HR SaaS USA" -m claude-3.5-sonnet   # via OpenRouter key

# custom OpenAI-compatible endpoint (Ollama, vLLM, Azure proxy, etc.)
leadgen search "cafes NYC" --provider custom --base-url http://localhost:11434/v1 --api-key ollama -m llama3.2

# interactive
leadgen
```

---

## Popular models

| Shortcut | Provider |
|----------|----------|
| `gpt-4o`, `gpt-4o-mini`, `gpt-4.1`, `o3-mini` | OpenAI |
| `gemini-2.0-flash`, `gemini-1.5-pro` | Google |
| `llama-3.3-70b` | Groq |
| `deepseek-chat` | DeepSeek |
| `mistral-large` | Mistral |
| `claude-3.5-sonnet`, `claude-sonnet-4` | OpenRouter |

```bash
leadgen models
```

---

## How it works

1. You type **keywords**  
2. Live **web search** finds public company pages  
3. Your chosen **LLM** scores leads + drafts outreach  
4. Exports **CSV / JSON** to `output/`

---

## Flags

| Flag | Meaning |
|------|---------|
| `-n / --count` | Max leads |
| `-m / --model` | Model name or famous shortcut |
| `-p / --provider` | openai, groq, gemini, deepseek, openrouter, mistral, custom |
| `--base-url` | Custom API base URL |
| `--api-key` | Pass key on CLI (prefer env for safety) |
| `-g / --geo` | Geography filter |
| `--min-score` | Drop weak leads |

---

## Ethics

- Public sources only  
- No invented private emails  
- Verify before outreach  
- Respect spam / privacy laws  

---

## Credits

**LeadGen AI**  
**Developed by Gyan Ranjan**  
https://github.com/Gyan4589/leadgen-ai
