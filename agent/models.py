from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class IdealCustomerProfile(BaseModel):
    """Structured ideal customer profile derived from the user's product pitch."""

    product_summary: str = Field(description="What you sell, in 1-2 sentences")
    target_industries: list[str] = Field(default_factory=list)
    company_sizes: list[str] = Field(
        default_factory=list,
        description="e.g. startup, SMB, mid-market, enterprise",
    )
    geographies: list[str] = Field(default_factory=list)
    buyer_titles: list[str] = Field(
        default_factory=list,
        description="Decision-maker roles to target",
    )
    pain_points: list[str] = Field(default_factory=list)
    buying_signals: list[str] = Field(
        default_factory=list,
        description="Public signals that indicate a good fit",
    )
    disqualifiers: list[str] = Field(default_factory=list)
    search_queries: list[str] = Field(
        default_factory=list,
        description="Web search queries to find matching companies",
    )
    value_proposition: str = ""


class Lead(BaseModel):
    company_name: str
    website: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    contact_name: Optional[str] = None
    contact_title: Optional[str] = None
    contact_email: Optional[str] = None
    linkedin_url: Optional[str] = None
    source_url: Optional[str] = None
    buying_signals: list[str] = Field(default_factory=list)
    fit_score: int = Field(ge=0, le=100, default=0)
    fit_reason: str = ""
    outreach_subject: str = ""
    outreach_email: str = ""
    next_action: str = ""


class LeadBatch(BaseModel):
    leads: list[Lead] = Field(default_factory=list)
    research_notes: str = ""


class LeadRunResult(BaseModel):
    icp: IdealCustomerProfile
    leads: list[Lead]
    research_notes: str = ""
    query: str = ""
