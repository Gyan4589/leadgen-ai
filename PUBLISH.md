# How to publish LeadGen AI so anyone can use it

**Developed by Gyan Ranjan**

There are **3 good ways**. Most people start with **GitHub**, then add **PyPI**.

---

## Option A — GitHub (easiest, free)

Anyone installs with:

```bash
pip install git+https://github.com/YOUR_USERNAME/leadgen-ai.git
leadgen search "dental clinics Mumbai" -n 5
```

### Steps

1. Create a free GitHub account: https://github.com/signup  
2. Create a **new public repo** named e.g. `leadgen-ai`  
3. In PowerShell:

```powershell
cd "$env:USERPROFILE\OneDrive\Desktop\papa\lead_agent"

# Never commit secrets
# .env is already in .gitignore

git init
git add .
git status   # confirm .env and output/ are NOT listed
git commit -m "Initial release: LeadGen AI by Gyan Ranjan"

# Create repo on GitHub first, then:
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/leadgen-ai.git
git push -u origin main
```

4. Share this link with users:

```
https://github.com/YOUR_USERNAME/leadgen-ai
```

**Users need:**
- Python 3.10+
- Their own `XAI_API_KEY` from https://console.x.ai

---

## Option B — PyPI (best: `pip install leadgen-ai`)

Anyone installs with:

```bash
pip install leadgen-ai
leadgen --help
```

### One-time setup

1. Create account: https://pypi.org/account/register/  
2. Enable 2FA on PyPI  
3. Create an **API token**: Account → API tokens → “Entire account” or project-scoped  
4. Install build tools:

```powershell
cd "$env:USERPROFILE\OneDrive\Desktop\papa\lead_agent"
.\.venv\Scripts\activate
pip install build twine
```

### Build the package

```powershell
python -m build
```

Creates `dist/leadgen_ai-1.1.0-py3-none-any.whl` and a `.tar.gz`.

### Upload to TestPyPI first (safe practice)

```powershell
# token form: pypi-AgEIcHl...
twine upload --repository testpypi dist/*
```

Test install:

```powershell
pip install -i https://test.pypi.org/simple/ leadgen-ai
```

### Upload to real PyPI

```powershell
twine upload dist/*
```

When prompted for password, paste the **API token** (username can be `__token__`).

### After publish, anyone runs

```bash
pip install leadgen-ai
set XAI_API_KEY=their_key_here   # Windows
leadgen search "real estate agents Delhi" -n 10
```

### Name taken on PyPI?

Edit `name` in `pyproject.toml`, e.g.:

```toml
name = "leadgen-ai-gyan"
```

Then rebuild and upload again.

---

## Option C — Windows `.exe` (no Python for users)

Good for non-technical users.

```powershell
cd "$env:USERPROFILE\OneDrive\Desktop\papa\lead_agent"
.\.venv\Scripts\activate
pip install pyinstaller
pyinstaller --onefile --name leadgen main.py
```

Share `dist\leadgen.exe`. Users still need `XAI_API_KEY` set in their environment or a `.env` next to the exe.

Upload the exe to GitHub **Releases**.

---

## What every user must have

| Item | Why |
|------|-----|
| Your CLI package | The tool |
| `XAI_API_KEY` | Calls Grok + web search (their key / their bill) |
| Internet | Live lead research |

**Never** put your own API key in the published package.

---

## Recommended path for you

| Step | Action |
|------|--------|
| 1 | Put code on **GitHub** (public) |
| 2 | Update `Homepage` URLs in `pyproject.toml` |
| 3 | Publish to **PyPI** |
| 4 | Share: `pip install leadgen-ai` |
| 5 | Optional: GitHub Release + `.exe` for Windows |

---

## Marketing one-liner

> **LeadGen AI** by **Gyan Ranjan** — type any keywords, get real sales leads.  
> `pip install leadgen-ai`

---

## Checklist before going public

- [ ] No `.env` or API keys in git  
- [ ] No personal lead CSVs in the repo (keep `output/` gitignored)  
- [ ] README has install + usage  
- [ ] LICENSE present (MIT included)  
- [ ] Version number in `pyproject.toml`  
- [ ] Test: `pip install .` then `leadgen --help` locally  

Local test before publish:

```powershell
cd "$env:USERPROFILE\OneDrive\Desktop\papa\lead_agent"
pip install .
leadgen --help
leadgen search "cafes Bangalore" -n 3
```
