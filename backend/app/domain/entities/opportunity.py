from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal

from app.domain.enums import LocationType, OpportunityType


@dataclass
class Opportunity:
    """
    Central entity — represents a single opportunity posting.

    Design notes:
    - `fingerprint` is a content hash used for deduplication (see Fingerprint value object).
    - `summary` is AI-generated after ingestion; stored so we don't re-call the LLM.
    - `raw_data` preserves the original scraped payload so we can re-parse without re-scraping.
    - `organization_id` is denormalized from source for fast filtering without joins.
    - `professor_id` is nullable — set only for professor-page and lab sources.
    - All date fields are nullable because postings often omit them.
    """

    title: str
    opportunity_type: OpportunityType
    source_id: int
    url: str
    fingerprint: str

    id: int | None = None
    organization_id: int | None = None
    professor_id: int | None = None
    description: str = ""
    summary: str = ""               # AI-generated; empty until enrichment runs
    location: str = ""              # raw string from posting
    location_type: LocationType = LocationType.NOT_SPECIFIED
    city: str = ""
    country: str = ""
    stipend_amount: Decimal | None = None
    stipend_currency: str = "USD"
    application_deadline: date | None = None
    start_date: date | None = None
    duration_weeks: int | None = None
    requirements: str = ""          # raw requirements text
    is_active: bool = True
    raw_data: dict = field(default_factory=dict)    # original scrape payload
    metadata: dict = field(default_factory=dict)    # flexible extra fields
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def is_deadline_soon(self, days: int = 7) -> bool:
        if self.application_deadline is None:
            return False
        from datetime import date as _date, timedelta
        return self.application_deadline <= _date.today() + timedelta(days=days)

    def __str__(self) -> str:
        return f"{self.title} [{self.opportunity_type}]"
