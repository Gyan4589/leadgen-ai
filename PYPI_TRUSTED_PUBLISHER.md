# PyPI Trusted Publisher form — fill exactly like this

**Developed by Gyan Ranjan**  
Repo: https://github.com/Gyan4589/leadgen-ai

## PyPI form fields (copy-paste)

| Field | Value |
|--------|--------|
| **Owner** (if asked) | `Gyan4589` |
| **Repository name (required)** | `leadgen-ai` |
| **Workflow name (required)** | `workflow.yml` |
| **Environment name (optional)** | `pypi` |

> Use **`leadgen-ai`** (not `leadsgen-ai`). That is the real GitHub repo name.

### Full trusted publisher (GitHub) usually looks like:

- **PyPI Project Name:** `leadgen-ai` (create pending publisher if project not on PyPI yet)
- **Owner:** `Gyan4589`
- **Repository name:** `leadgen-ai`
- **Workflow name:** `workflow.yml`
- **Environment name:** `pypi`

---

## Steps on PyPI

1. Log in: https://pypi.org  
2. If the project does **not** exist yet:  
   https://pypi.org/manage/account/publishing/  
   → **Add a new pending publisher**  
3. If project already exists: project settings → **Publishing**  
4. Fill the form with the values above  
5. Save  

---

## Steps on GitHub (environment)

1. Open: https://github.com/Gyan4589/leadgen-ai/settings/environments  
2. **New environment** → name: `pypi`  
3. (Optional but recommended) add protection rules, e.g. required reviewers  
4. Save  

Workflow file path (must match):

```
.github/workflows/workflow.yml
```

---

## Publish after setup

**Option A — Release (recommended)**  
GitHub → Releases → Draft a new release → tag `v1.1.0` → Publish release  

**Option B — Manual**  
Actions → **Publish to PyPI** → Run workflow  

Then install:

```bash
pip install leadgen-ai
leadgen --help
```
