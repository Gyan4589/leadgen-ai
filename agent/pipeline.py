from __future__ import annotations

from .branding import CREDIT
from .export import export_all
from .llm import LLM
from .models import IdealCustomerProfile, Lead, LeadBatch, LeadRunResult
from .config import Settings
from .search import multi_search


ICP_SYSTEM = """You are a senior B2B sales strategist and ICP designer.
The user may give a full product offer OR just simple search keywords
(e.g. "dental clinics Mumbai", "SaaS HR software US", "real estate agents Texas").

Turn whatever they typed into a precise Ideal Customer Profile that a research
agent can use to find real companies.

Rules:
- If input is keywords only, infer the most likely B2B/B2C lead-hunting intent.
- Be specific and actionable (real industries, titles, signals).
- Prefer public, ethical buying signals (hiring, tech stack, expansion, funding, launches).
- search_queries must be concrete web-search queries that surface company names and sites.
  Expand keywords into 5–10 strong queries (city + industry, "best companies", directories, etc.).
- Never invent private contact data.
"""

KEYWORD_RESEARCH_SYSTEM = f"""You are an expert lead research agent.
Product: LeadGen AI — {CREDIT}.

You will receive SEARCH KEYWORDS plus LIVE WEB SEARCH RESULTS.
Find REAL companies / businesses that match those keywords using the search results.

Hard rules:
1. Prefer companies that appear in the provided web search results.
2. Prefer real, currently operating businesses with public websites.
3. Only include facts grounded in the search snippets/URLs or clearly public knowledge.
4. Do NOT invent email addresses, phone numbers, or private personal data.
5. contact_email: only if clearly public. Otherwise null.
6. contact_name / contact_title: only if publicly listed. Otherwise null.
7. For each lead, cite a source_url from the search results when possible.
8. Score fit_score 0-100 based on keyword match + quality of public data.
9. Write a short personalized outreach_subject and outreach_email (plain text, 80-120 words).
10. next_action: concrete CRM step.
11. Prefer quality over quantity. No duplicate companies.
12. Return JSON only matching the schema.
13. research_notes: what you used + caveats.
"""

RESEARCH_SYSTEM = f"""You are an expert B2B lead research agent.
Product: LeadGen AI — {CREDIT}.

Find REAL companies that match the Ideal Customer Profile using the live web results.

Hard rules:
1. Prefer companies from the web search results.
2. Only include facts grounded in public sources / search snippets.
3. Do NOT invent private contact data.
4. contact_email / personal details only if clearly public; else null.
5. Cite source_url per lead when possible.
6. Score fit_score 0-100. Write short outreach email + next_action.
7. Return JSON only matching the schema.
"""

ENRICH_SYSTEM = f"""You are a B2B outbound copywriter and lead qualifier.
Product: LeadGen AI — {CREDIT}.

Given search intent / ICP and candidate leads, refine scores, tighten fit reasons,
and polish outreach emails. Do not invent new companies or private contacts.
Keep only leads that still meet the bar. Return JSON only.
"""


class LeadAgent:
    """Keyword or offer → web research → score → outreach → export."""

    def __init__(self, settings: Settings | None = None, llm: LLM | None = None):
        self.settings = settings or Settings.from_env()
        self.llm = llm or LLM(self.settings)

    def build_icp(
        self,
        offer: str,
        *,
        industry: str | None = None,
        geo: str | None = None,
        company_size: str | None = None,
        extra: str | None = None,
        keywords_mode: bool = False,
    ) -> IdealCustomerProfile:
        constraints = []
        if industry:
            constraints.append(f"Preferred industries: {industry}")
        if geo:
            constraints.append(f"Target geography: {geo}")
        if company_size:
            constraints.append(f"Company size focus: {company_size}")
        if extra:
            constraints.append(f"Extra notes: {extra}")

        if keywords_mode:
            user = (
                "The user entered SEARCH KEYWORDS (not necessarily a product pitch).\n"
                f"Keywords: {offer.strip()}\n\n"
                "Build an ICP and expand into strong web search queries to find matching leads."
            )
        else:
            user = f"Product / offer / keywords:\n{offer.strip()}\n"
        if constraints:
            user += "\nConstraints:\n- " + "\n- ".join(constraints)

        return self.llm.complete_json(
            ICP_SYSTEM,
            user,
            IdealCustomerProfile,
            use_web_search=False,
        )

    def research_by_keywords(
        self,
        keywords: str,
        *,
        count: int = 10,
        min_score: int | None = None,
        geo: str | None = None,
        industry: str | None = None,
        company_size: str | None = None,
    ) -> LeadBatch:
        min_score = self.settings.min_score if min_score is None else min_score
        filters = []
        if geo:
            filters.append(f"Geography focus: {geo}")
        if industry:
            filters.append(f"Industry focus: {industry}")
        if company_size:
            filters.append(f"Company size: {company_size}")

        filter_block = ""
        if filters:
            filter_block = "\nFilters:\n- " + "\n- ".join(filters)

        queries = [keywords.strip()]
        if geo:
            queries.append(f"{keywords} {geo}")
        if industry:
            queries.append(f"{keywords} {industry}")
        queries.extend(
            [
                f"best {keywords} companies list",
                f"{keywords} directory",
                f"top {keywords}",
            ]
        )

        web_brief = ""
        if self.settings.use_web_search:
            web_brief = multi_search(queries[:6], max_per_query=5)

        user = f"""Search keywords: {keywords.strip()}
{filter_block}

LIVE WEB SEARCH RESULTS:
{web_brief}

Find up to {count} high-quality real business leads matching these keywords.

Requirements:
- Return at most {count} leads
- fit_score should be >= {min_score} when possible; drop weak leads
- No duplicate companies
- research_notes: what you used + caveats
"""
        batch = self.llm.complete_json(
            KEYWORD_RESEARCH_SYSTEM,
            user,
            LeadBatch,
            use_web_search=False,
            temperature=0.25,
        )
        batch.leads = [
            lead for lead in batch.leads if lead.fit_score >= min_score
        ][:count]
        return batch

    def research_leads(
        self,
        icp: IdealCustomerProfile,
        *,
        count: int = 10,
        min_score: int | None = None,
    ) -> LeadBatch:
        min_score = self.settings.min_score if min_score is None else min_score
        queries = list(icp.search_queries[:8]) or [icp.product_summary]
        web_brief = multi_search(queries, max_per_query=5) if self.settings.use_web_search else ""
        user = f"""Find up to {count} high-quality B2B leads.

ICP JSON:
{icp.model_dump_json(indent=2)}

LIVE WEB SEARCH RESULTS:
{web_brief}

Requirements:
- Return at most {count} leads
- Each fit_score should be >= {min_score} when possible; drop weak leads
- Prefer diversity across companies (no duplicates)
- Research notes: brief summary + caveats
"""
        batch = self.llm.complete_json(
            RESEARCH_SYSTEM,
            user,
            LeadBatch,
            use_web_search=False,
            temperature=0.25,
        )
        batch.leads = [
            lead for lead in batch.leads if lead.fit_score >= min_score
        ][:count]
        return batch

    def refine_leads(
        self,
        context: str,
        leads: list[Lead],
        *,
        min_score: int | None = None,
    ) -> list[Lead]:
        if not leads:
            return []
        min_score = self.settings.min_score if min_score is None else min_score
        payload = LeadBatch(leads=leads, research_notes="refine pass")
        user = f"""Search intent / context:
{context}

Leads to refine:
{payload.model_dump_json(indent=2)}

Keep leads with fit_score >= {min_score}. Improve outreach personalization.
"""
        refined = self.llm.complete_json(
            ENRICH_SYSTEM,
            user,
            LeadBatch,
            use_web_search=False,
            temperature=0.3,
        )
        return [lead for lead in refined.leads if lead.fit_score >= min_score]

    def search_keywords(
        self,
        keywords: str,
        *,
        count: int = 10,
        industry: str | None = None,
        geo: str | None = None,
        company_size: str | None = None,
        min_score: int | None = None,
        refine: bool = True,
        export: bool = True,
    ) -> LeadRunResult:
        min_score = self.settings.min_score if min_score is None else min_score
        keywords = keywords.strip()

        icp = self.build_icp(
            keywords,
            industry=industry,
            geo=geo,
            company_size=company_size,
            keywords_mode=True,
        )

        batch = self.research_by_keywords(
            keywords,
            count=count,
            min_score=min_score,
            geo=geo,
            industry=industry,
            company_size=company_size,
        )
        leads = batch.leads
        if refine and leads:
            leads = self.refine_leads(keywords, leads, min_score=min_score)

        leads = sorted(leads, key=lambda l: l.fit_score, reverse=True)
        result = LeadRunResult(
            icp=icp,
            leads=leads,
            research_notes=batch.research_notes,
            query=keywords,
        )
        if export:
            export_all(result)
        return result

    def run(
        self,
        offer: str,
        *,
        count: int = 10,
        industry: str | None = None,
        geo: str | None = None,
        company_size: str | None = None,
        extra: str | None = None,
        min_score: int | None = None,
        refine: bool = True,
        export: bool = True,
    ) -> LeadRunResult:
        min_score = self.settings.min_score if min_score is None else min_score

        icp = self.build_icp(
            offer,
            industry=industry,
            geo=geo,
            company_size=company_size,
            extra=extra,
        )
        batch = self.research_leads(icp, count=count, min_score=min_score)
        leads = batch.leads
        if refine and leads:
            leads = self.refine_leads(icp.model_dump_json(), leads, min_score=min_score)

        leads = sorted(leads, key=lambda l: l.fit_score, reverse=True)
        result = LeadRunResult(
            icp=icp,
            leads=leads,
            research_notes=batch.research_notes,
            query=offer,
        )
        if export:
            export_all(result)
        return result
