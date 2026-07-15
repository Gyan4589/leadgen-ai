"""Provider-agnostic web search so any LLM can research real leads."""

from __future__ import annotations


def web_search(query: str, max_results: int = 8) -> list[dict[str, str]]:
    """Search the public web. Returns [{title, href, body}, ...]."""
    query = (query or "").strip()
    if not query:
        return []

    # Prefer new package name, fall back to older
    try:
        from ddgs import DDGS  # type: ignore
    except ImportError:
        try:
            from duckduckgo_search import DDGS  # type: ignore
        except ImportError:
            return []

    results: list[dict[str, str]] = []
    try:
        with DDGS() as ddgs:
            for item in ddgs.text(query, max_results=max_results):
                results.append(
                    {
                        "title": str(item.get("title") or ""),
                        "href": str(item.get("href") or item.get("link") or ""),
                        "body": str(item.get("body") or item.get("snippet") or ""),
                    }
                )
    except Exception:
        return results
    return results


def multi_search(queries: list[str], max_per_query: int = 5) -> str:
    """Run several queries and format a research brief for the LLM."""
    blocks: list[str] = []
    seen: set[str] = set()
    for q in queries:
        q = q.strip()
        if not q:
            continue
        hits = web_search(q, max_results=max_per_query)
        if not hits:
            continue
        lines = [f"### Query: {q}"]
        for h in hits:
            href = h.get("href") or ""
            if href in seen:
                continue
            if href:
                seen.add(href)
            lines.append(
                f"- {h.get('title') or 'Result'}\n"
                f"  URL: {href}\n"
                f"  Snippet: {h.get('body') or ''}"
            )
        if len(lines) > 1:
            blocks.append("\n".join(lines))
    if not blocks:
        return (
            "(No live web results available. Infer carefully from public knowledge "
            "and mark uncertain fields null. Prefer well-known real companies.)"
        )
    return "\n\n".join(blocks)
