"""
ScrapeContext — the state carrier that flows through every pipeline stage.

Each stage reads from it and appends to it; nothing is ever replaced,
so a stage failure cannot corrupt the work of prior stages.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal

from app.domain.entities.opportunity import Opportunity
from app.domain.entities.scrape_job import ScrapeJob
from app.domain.entities.source import Source
from app.domain.enums import OpportunityType
from app.domain.ports.scraper_port import RawPosting
from app.domain.value_objects.location import Location
from app.infrastructure.scrapers.metrics import ScrapeMetrics


@dataclass
class FetchedPage:
    """A single HTTP response — the output of one fetch call."""

    url: str
    content: str          # raw text (HTML, XML, JSON, …)
    status_code: int
    content_type: str
    fetched_at: datetime

    @property
    def is_ok(self) -> bool:
        return 200 <= self.status_code < 300

    @property
    def is_html(self) -> bool:
        return "text/html" in self.content_type

    @property
    def is_xml(self) -> bool:
        return any(t in self.content_type for t in ["xml", "rss", "atom"])


@dataclass
class NormalizedPosting:
    """
    A RawPosting after normalization — parsed dates, typed enums, structured location.

    Carries the original RawPosting so the PersistStage can access raw_data.
    """

    raw: RawPosting
    fingerprint: str
    opportunity_type: OpportunityType
    parsed_deadline: date | None
    parsed_start_date: date | None
    stipend_amount: Decimal | None
    stipend_currency: str
    location: Location

    # Set by FingerprintStage after repo lookup
    is_duplicate: bool = False
    # Set by NormalizeStage or ValidateStage if content is clearly unusable
    is_rejected: bool = False
    rejection_reason: str | None = None


@dataclass
class ScrapeContext:
    """Carries all pipeline state from Fetch through Emit."""

    source: Source
    job: ScrapeJob

    fetched_pages: list[FetchedPage] = field(default_factory=list)
    raw_postings: list[RawPosting] = field(default_factory=list)
    normalized_postings: list[NormalizedPosting] = field(default_factory=list)
    persisted_opportunities: list[Opportunity] = field(default_factory=list)

    metrics: ScrapeMetrics = field(default_factory=ScrapeMetrics)
    errors: list[Exception] = field(default_factory=list)
