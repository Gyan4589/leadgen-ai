#!/usr/bin/env python3
"""LeadGen AI — search any keywords, get real sales leads.

Works with any OpenAI-compatible API (OpenAI, Groq, Gemini, DeepSeek, OpenRouter, …).
Developed by Gyan Ranjan.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from agent.branding import APP_NAME, CREDIT, VERSION, banner_lines
from agent.config import Settings
from agent.export import export_all, merge_all_csvs, load_csv_rows
from agent.models import LeadRunResult
from agent.models_catalog import list_models_help
from agent.pipeline import LeadAgent

app = typer.Typer(
    name="leadgen",
    help=f"{APP_NAME} — keywords → sales leads. Any AI API. {CREDIT}.",
    add_completion=False,
    no_args_is_help=False,
)
console = Console()

# Shared optional AI options (Typer doesn't support inheritance easily — pass via context)
_AI_OPTS: dict = {}


def _banner(settings: Settings | None = None) -> None:
    extra = ""
    if settings:
        extra = (
            f"\n[dim]Provider:[/] {settings.provider}  "
            f"[dim]Model:[/] {settings.model}\n"
            f"[dim]API:[/] {settings.base_url}"
        )
    console.print(
        Panel.fit(banner_lines() + extra, border_style="cyan", title=APP_NAME)
    )


def _print_icp(icp) -> None:
    console.print(
        Panel.fit(
            f"[bold]{icp.product_summary}[/bold]\n\n"
            f"[cyan]Industries:[/] {', '.join(icp.target_industries) or '—'}\n"
            f"[cyan]Sizes:[/] {', '.join(icp.company_sizes) or '—'}\n"
            f"[cyan]Geo:[/] {', '.join(icp.geographies) or '—'}\n"
            f"[cyan]Buyers:[/] {', '.join(icp.buyer_titles) or '—'}\n"
            f"[cyan]Value prop:[/] {icp.value_proposition or '—'}",
            title="Search profile",
            border_style="magenta",
        )
    )
    if icp.search_queries:
        console.print("[bold]Expanded search queries[/]")
        for q in icp.search_queries[:8]:
            console.print(f"  • {q}")
    console.print()


def _print_leads(leads) -> None:
    if not leads:
        console.print("[yellow]No leads found. Try different keywords.[/yellow]")
        return

    table = Table(title=f"Leads  ·  {CREDIT}", show_lines=True)
    table.add_column("#", style="dim", width=3)
    table.add_column("Company", style="bold")
    table.add_column("Score", justify="right")
    table.add_column("Industry")
    table.add_column("Location")
    table.add_column("Contact")
    table.add_column("Why it matches")

    for i, lead in enumerate(leads, 1):
        contact = lead.contact_name or "—"
        if lead.contact_title:
            contact = f"{contact}\n[dim]{lead.contact_title}[/dim]"
        score_style = (
            "green" if lead.fit_score >= 75 else "yellow" if lead.fit_score >= 50 else "red"
        )
        table.add_row(
            str(i),
            f"{lead.company_name}\n[dim]{lead.website or ''}[/dim]",
            f"[{score_style}]{lead.fit_score}[/{score_style}]",
            lead.industry or "—",
            lead.location or "—",
            contact,
            (lead.fit_reason or "")[:120],
        )
    console.print(table)

    for lead in leads:
        if not lead.outreach_email:
            continue
        console.print(
            Panel(
                f"[bold]Subject:[/] {lead.outreach_subject}\n\n{lead.outreach_email}\n\n"
                f"[dim]Next:[/] {lead.next_action or '—'}\n"
                f"[dim]Source:[/] {lead.source_url or '—'}",
                title=f"Outreach · {lead.company_name}",
                border_style="blue",
            )
        )


def _get_agent(
    *,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
) -> LeadAgent:
    try:
        settings = Settings.from_env(
            provider=provider or _AI_OPTS.get("provider"),
            model=model or _AI_OPTS.get("model"),
            base_url=base_url or _AI_OPTS.get("base_url"),
            api_key=api_key or _AI_OPTS.get("api_key"),
        )
    except RuntimeError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc
    return LeadAgent(settings)


def _save_and_report(result: LeadRunResult, out_dir: Optional[Path], no_export: bool) -> None:
    if result.research_notes:
        console.print(Panel(result.research_notes, title="Research notes", border_style="dim"))

    _print_leads(result.leads)

    if not no_export and result.leads:
        paths = export_all(result, out_dir)
        console.print(
            f"\n[green]Saved[/] CSV → {paths['csv']}\n"
            f"[green]Saved[/] JSON → {paths['json']}\n"
            f"[green]Master[/] all leads → {paths['all']}"
        )

    console.print(
        f"\n[bold]Done.[/] {len(result.leads)} lead(s).  [dim]{CREDIT} · {APP_NAME} v{VERSION}[/]"
    )


@app.callback(invoke_without_command=True)
def root(
    ctx: typer.Context,
    keywords: Optional[str] = typer.Option(
        None,
        "--keywords",
        "-k",
        help="Search keywords (e.g. 'dental clinics Delhi', 'HR SaaS US').",
    ),
    provider: Optional[str] = typer.Option(
        None,
        "--provider",
        "-p",
        help="AI provider: openai, groq, gemini, deepseek, openrouter, mistral, xai, custom",
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model",
        "-m",
        help="Model name, e.g. gpt-4o, gemini-2.0-flash, llama-3.3-70b, claude-3.5-sonnet",
    ),
    base_url: Optional[str] = typer.Option(
        None,
        "--base-url",
        help="Custom OpenAI-compatible API base URL",
    ),
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        help="API key (or set OPENAI_API_KEY / any provider key in env)",
    ),
):
    """LeadGen AI by Gyan Ranjan — any AI API, keyword lead search."""
    _AI_OPTS["provider"] = provider
    _AI_OPTS["model"] = model
    _AI_OPTS["base_url"] = base_url
    _AI_OPTS["api_key"] = api_key

    if ctx.invoked_subcommand is not None:
        return
    if keywords:
        ctx.invoke(
            search,
            keywords=keywords,
            count=10,
            industry=None,
            geo=None,
            company_size=None,
            min_score=50,
            no_refine=False,
            no_export=False,
            out_dir=None,
            provider=provider,
            model=model,
            base_url=base_url,
            api_key=api_key,
        )
        return
    ctx.invoke(chat)


@app.command("models")
def models_cmd():
    """List popular models and supported providers."""
    console.print(Panel.fit(banner_lines(), border_style="cyan"))
    console.print(list_models_help())
    console.print(
        "\n[dim]Example:[/]\n"
        "  set OPENAI_API_KEY=sk-...\n"
        "  leadgen search \"dental clinics Mumbai\" -m gpt-4o -n 5\n"
        "  leadgen search \"gyms Delhi\" -p groq -m llama-3.3-70b\n"
        f"\n[magenta]{CREDIT}[/]"
    )


@app.command("search")
def search(
    keywords: str = typer.Argument(
        ...,
        help="Any keywords: industry, city, niche, role… e.g. 'gyms Mumbai' or 'AI startups India'.",
    ),
    count: int = typer.Option(10, "--count", "-n", help="Max leads to return."),
    industry: Optional[str] = typer.Option(None, "--industry", "-i", help="Industry filter."),
    geo: Optional[str] = typer.Option(None, "--geo", "-g", help="Geography filter."),
    company_size: Optional[str] = typer.Option(
        None, "--size", "-s", help="e.g. SMB, mid-market, enterprise"
    ),
    min_score: int = typer.Option(40, "--min-score", help="Drop leads below this score."),
    no_refine: bool = typer.Option(False, "--no-refine", help="Skip polish pass (faster)."),
    no_export: bool = typer.Option(False, "--no-export", help="Do not write CSV/JSON."),
    out_dir: Optional[Path] = typer.Option(None, "--out", help="Output directory."),
    provider: Optional[str] = typer.Option(None, "--provider", "-p"),
    model: Optional[str] = typer.Option(None, "--model", "-m"),
    base_url: Optional[str] = typer.Option(None, "--base-url"),
    api_key: Optional[str] = typer.Option(None, "--api-key"),
):
    """Search any keywords and generate real business leads."""
    agent = _get_agent(provider=provider, model=model, base_url=base_url, api_key=api_key)
    _banner(agent.settings)
    console.print(f"[bold]Keywords:[/] {keywords}\n")

    with console.status("[bold green]Understanding keywords & building search profile..."):
        icp = agent.build_icp(
            keywords,
            industry=industry,
            geo=geo,
            company_size=company_size,
            keywords_mode=True,
        )
    _print_icp(icp)

    with console.status(
        "[bold green]Searching the web & generating leads (may take a minute)..."
    ):
        batch = agent.research_by_keywords(
            keywords,
            count=count,
            min_score=min_score,
            geo=geo,
            industry=industry,
            company_size=company_size,
        )

    leads = batch.leads
    if not no_refine and leads:
        with console.status("[bold green]Scoring & writing outreach..."):
            leads = agent.refine_leads(keywords, leads, min_score=min_score)

    leads = sorted(leads, key=lambda l: l.fit_score, reverse=True)
    result = LeadRunResult(
        icp=icp,
        leads=leads,
        research_notes=batch.research_notes,
        query=keywords,
    )
    _save_and_report(result, out_dir, no_export)


@app.command()
def find(
    offer: str = typer.Argument(..., help="Product pitch or keywords."),
    count: int = typer.Option(10, "--count", "-n"),
    industry: Optional[str] = typer.Option(None, "--industry", "-i"),
    geo: Optional[str] = typer.Option(None, "--geo", "-g"),
    company_size: Optional[str] = typer.Option(None, "--size", "-s"),
    extra: Optional[str] = typer.Option(None, "--extra", "-e"),
    min_score: int = typer.Option(50, "--min-score"),
    no_refine: bool = typer.Option(False, "--no-refine"),
    no_export: bool = typer.Option(False, "--no-export"),
    out_dir: Optional[Path] = typer.Option(None, "--out"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p"),
    model: Optional[str] = typer.Option(None, "--model", "-m"),
    base_url: Optional[str] = typer.Option(None, "--base-url"),
    api_key: Optional[str] = typer.Option(None, "--api-key"),
):
    """Find leads from a product offer or free-text description."""
    agent = _get_agent(provider=provider, model=model, base_url=base_url, api_key=api_key)
    _banner(agent.settings)
    console.print(f"[dim]Query:[/] {offer}\n")

    extra_bits = extra or ""
    query = f"{offer}\n{extra_bits}".strip()
    with console.status("[bold green]Building profile from your query..."):
        icp = agent.build_icp(
            query,
            industry=industry,
            geo=geo,
            company_size=company_size,
            extra=extra,
            keywords_mode=True,
        )
    _print_icp(icp)

    with console.status("[bold green]Searching the web for leads..."):
        batch = agent.research_by_keywords(
            query,
            count=count,
            min_score=min_score,
            geo=geo,
            industry=industry,
            company_size=company_size,
        )

    leads = batch.leads
    if not no_refine and leads:
        with console.status("[bold green]Refining scores and outreach..."):
            leads = agent.refine_leads(query, leads, min_score=min_score)

    leads = sorted(leads, key=lambda l: l.fit_score, reverse=True)
    result = LeadRunResult(
        icp=icp,
        leads=leads,
        research_notes=batch.research_notes,
        query=offer,
    )
    _save_and_report(result, out_dir, no_export)


@app.command("merge-all")
def merge_all(
    out_dir: Optional[Path] = typer.Option(None, "--out", help="Output directory."),
):
    """Merge every leads_*.csv into output/all_leads.csv."""
    path = merge_all_csvs(out_dir)
    rows = load_csv_rows(path)
    console.print(f"[green]Merged {len(rows)} unique lead(s) →[/] {path}")
    console.print(f"[dim]{CREDIT}[/]")
    if rows:
        table = Table(title=f"All Leads · {CREDIT}")
        table.add_column("#", style="dim", width=3)
        table.add_column("Company", style="bold")
        table.add_column("Score", justify="right")
        table.add_column("Industry")
        table.add_column("Contact")
        for i, row in enumerate(rows, 1):
            table.add_row(
                str(i),
                row.get("company_name") or "—",
                str(row.get("fit_score") or "—"),
                row.get("industry") or "—",
                row.get("contact_name") or "—",
            )
        console.print(table)


@app.command("chat")
def chat():
    """Interactive: type any keywords, get leads."""
    agent = _get_agent()
    _banner(agent.settings)
    console.print(
        Panel.fit(
            "[bold]Type any keywords[/] to find leads.\n"
            "Examples:\n"
            "  • dental clinics Mumbai\n"
            "  • real estate agents Texas\n"
            "  • AI startups Bangalore\n"
            "  • corporate gifting companies USA\n"
            f"\n[dim]Works with OpenAI, Groq, Gemini, DeepSeek, OpenRouter, …[/]\n"
            f"[dim]{CREDIT}[/]",
            border_style="cyan",
            title="Keyword Lead Search",
        )
    )
    keywords = console.input("[bold cyan]Keywords[/] > ").strip()
    if not keywords:
        console.print("[red]Please enter some keywords.[/red]")
        raise typer.Exit(1)

    geo = console.input("Geo filter (optional, Enter to skip): ").strip() or None
    count_raw = console.input("How many leads? [8]: ").strip() or "8"
    try:
        count = max(1, min(25, int(count_raw)))
    except ValueError:
        count = 8

    search(
        keywords=keywords,
        count=count,
        industry=None,
        geo=geo,
        company_size=None,
        min_score=40,
        no_refine=False,
        no_export=False,
        out_dir=None,
        provider=_AI_OPTS.get("provider"),
        model=_AI_OPTS.get("model"),
        base_url=_AI_OPTS.get("base_url"),
        api_key=_AI_OPTS.get("api_key"),
    )


def main() -> None:
    if len(sys.argv) > 1:
        first = sys.argv[1]
        known = {
            "search",
            "find",
            "chat",
            "merge-all",
            "models",
            "--help",
            "-h",
            "--keywords",
            "-k",
            "--provider",
            "-p",
            "--model",
            "-m",
            "--base-url",
            "--api-key",
        }
        if first not in known and not first.startswith("-"):
            sys.argv.insert(1, "search")
    app()


if __name__ == "__main__":
    main()
