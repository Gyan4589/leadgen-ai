from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from .models import Lead, LeadRunResult

CSV_FIELDS = [
    "company_name",
    "website",
    "industry",
    "company_size",
    "location",
    "description",
    "contact_name",
    "contact_title",
    "contact_email",
    "linkedin_url",
    "source_url",
    "buying_signals",
    "fit_score",
    "fit_reason",
    "outreach_subject",
    "outreach_email",
    "next_action",
]


def default_output_dir() -> Path:
    root = Path(__file__).resolve().parent.parent / "output"
    root.mkdir(parents=True, exist_ok=True)
    return root


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _lead_to_row(lead: Lead) -> dict:
    row = lead.model_dump()
    signals = row.get("buying_signals") or []
    if isinstance(signals, list):
        row["buying_signals"] = "; ".join(str(s) for s in signals)
    return row


def export_csv(leads: list[Lead], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for lead in leads:
            writer.writerow(_lead_to_row(lead))
    return path


def export_json(result: LeadRunResult, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    return path


def _normalize_key(name: str, website: str | None = None) -> str:
    base = (name or "").strip().lower()
    site = (website or "").strip().lower().removeprefix("https://").removeprefix("http://").removeprefix("www.")
    site = site.rstrip("/")
    return f"{base}|{site}"


def load_csv_rows(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def merge_lead_rows(rows: Iterable[dict]) -> list[dict]:
    """Dedupe by company+website, keep highest fit_score."""
    best: dict[str, dict] = {}
    for row in rows:
        name = (row.get("company_name") or "").strip()
        if not name:
            continue
        key = _normalize_key(name, row.get("website"))
        try:
            score = int(float(row.get("fit_score") or 0))
        except (TypeError, ValueError):
            score = 0
        row = {**row, "fit_score": score}
        prev = best.get(key)
        if prev is None:
            best[key] = row
            continue
        try:
            prev_score = int(float(prev.get("fit_score") or 0))
        except (TypeError, ValueError):
            prev_score = 0
        if score >= prev_score:
            best[key] = row
    merged = list(best.values())
    merged.sort(key=lambda r: int(r.get("fit_score") or 0), reverse=True)
    return merged


def write_rows_csv(rows: list[dict], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            out = {k: row.get(k, "") for k in CSV_FIELDS}
            writer.writerow(out)
    return path


def merge_all_csvs(out_dir: Path | None = None) -> Path:
    """Merge every leads_*.csv in output/ into all_leads.csv (deduped)."""
    out = out_dir or default_output_dir()
    rows: list[dict] = []
    for path in sorted(out.glob("leads_*.csv")):
        rows.extend(load_csv_rows(path))
    # Also include existing master if present
    master = out / "all_leads.csv"
    if master.is_file():
        rows.extend(load_csv_rows(master))
    merged = merge_lead_rows(rows)
    return write_rows_csv(merged, master)


def append_to_master(leads: list[Lead], out_dir: Path | None = None) -> Path:
    out = out_dir or default_output_dir()
    master = out / "all_leads.csv"
    existing = load_csv_rows(master)
    new_rows = [_lead_to_row(lead) for lead in leads]
    merged = merge_lead_rows(existing + new_rows)
    return write_rows_csv(merged, master)


def export_all(result: LeadRunResult, out_dir: Path | None = None) -> dict[str, Path]:
    out = out_dir or default_output_dir()
    ts = stamp()
    csv_path = export_csv(result.leads, out / f"leads_{ts}.csv")
    json_path = export_json(result, out / f"leads_{ts}.json")
    master_path = append_to_master(result.leads, out)
    return {"csv": csv_path, "json": json_path, "all": master_path}
