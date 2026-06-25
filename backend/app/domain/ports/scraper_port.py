from dataclasses import dataclass, field
from typing import Any, Protocol

from app.domain.entities.source import Source
from app.domain.enums import OpportunityType


@dataclass
class RawPosting:
    """
    Normalised output from a SourceAdapter — one posting before enrichment.

    Every adapter is responsible for mapping its source-specific fields into
    this common shape. Unknown fields go into `extra`.
    """

    title: str
    url: str
    organization_name: str
    raw_html: str = ""
    description: str = ""
    location: str = ""
    opportunity_type: OpportunityType = OpportunityType.RESEARCH_INTERNSHIP
    application_deadline: str = ""   # raw string — parsed downstream
    start_date: str = ""
    requirements: str = ""
    stipend: str = ""
    professor_name: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


class SourceAdapter(Protocol):
    """
    Interface every scraper adapter must implement.

    One class per source type (or per specific site for custom logic).
    Register adapters in infrastructure/scrapers/registry.py.
    """

    async def fetch(self, source: Source) -> list[RawPosting]:
        """
        Fetch all current postings from the source.
        Returns an empty list (not raises) if the source is unreachable —
        the caller logs and records the failure in ScrapeJob.
        """
        ...

    async def is_reachable(self, source: Source) -> bool:
        """Quick connectivity check — used by the admin healthcheck panel."""
        ...
