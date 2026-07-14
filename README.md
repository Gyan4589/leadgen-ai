# LeadGen AI

**Search any keywords → get real sales leads**

**Developed by Gyan Ranjan**

Powered by Grok + live web search. Type simple keywords (or a full product pitch) and get scored companies, contacts (when public), and outreach drafts.

---

## Install (anyone)

### From PyPI (after you publish)

```bash
pip install leadgen-ai
```

### From GitHub

```bash
pip install git+https://github.com/Gyan4589/leadgen-ai.git
```

### From this folder (developers)

```powershell
cd lead_agent
pip install .
# or Windows helper:
.\install.ps1
```

Then:

```bash
leadgen
leadgen search "dental clinics Mumbai" -n 5
```

### API key (required)

Get a key at [console.x.ai](https://console.x.ai), then:

```bash
# Windows PowerShell
$env:XAI_API_KEY = "your_key"

# Or create a .env file next to where you run:
# XAI_API_KEY=your_key
```

---

## Quick start (Windows, local project)

```powershell
cd "$env:USERPROFILE\OneDrive\Desktop\papa\lead_agent"
.\install.ps1
```

Open a **new** PowerShell:

```powershell
leadgen
leadgen search "dental clinics Mumbai" -n 5
lead_agent
```

Or without install:

```powershell
.\run.ps1
.\leadgen.cmd search "gyms Delhi" -n 5
```

**Publish this CLI for the world?** See [PUBLISH.md](./PUBLISH.md).

You’ll be asked for keywords, e.g.:

- `dental clinics Mumbai`
- `real estate agents Texas`
- `AI startups Bangalore`
- `corporate gifting companies USA`

Or pass keywords directly:

```powershell
.\run.ps1 -Keywords "gyms Delhi" -Count 10
.\run.ps1 -Keywords "HR SaaS SMB" -Geo "United States" -Count 8
```

Double-click **`run.bat`** for the same interactive flow.

---

## Setup

```powershell
cd lead_agent
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Set `XAI_API_KEY` in `.env` ([console.x.ai](https://console.x.ai)), **or** stay signed into Grok Build/CLI (`~\.grok\auth.json` is used automatically).

---

## Commands

### Keyword search (main)

```bash
python main.py search "dental clinics Mumbai" -n 10
python main.py search "logistics companies India" --geo "India" -n 8
python main.py "AI startups Bangalore" -n 5
```

### Interactive

```bash
python main.py
# or
python main.py chat
```

### Product / offer mode

```bash
python main.py find "We sell invoice automation to logistics SMBs" -n 8
```

### Merge all runs

```bash
python main.py merge-all
```

→ `output/all_leads.csv` (deduped master list)

---

## Flags

| Flag | Meaning |
|------|---------|
| `-n / --count` | Max leads |
| `-g / --geo` | Geography filter |
| `-i / --industry` | Industry filter |
| `-s / --size` | Company size |
| `--min-score` | Drop weak leads (default 40 for search) |
| `--no-refine` | Faster, skip polish |
| `--out DIR` | Output folder |

---

## Output

Each run saves:

- `output/leads_YYYYMMDD_HHMMSS.csv`
- `output/leads_YYYYMMDD_HHMMSS.json`
- `output/all_leads.csv` (all runs combined)

---

## Ethics

- Public web sources only  
- No invented private emails  
- Verify before outreach  
- Respect local spam / privacy laws  

---

## Credits

**LeadGen AI**  
**Developed by Gyan Ranjan**  
Built with xAI Grok
