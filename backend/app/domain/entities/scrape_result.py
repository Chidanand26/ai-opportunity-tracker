from dataclasses import dataclass
from datetime import datetime


@dataclass
class ScrapeResult:
    """
    One raw posting found during a ScrapeJob, before dedup/enrichment.

    Persisted immediately after scraping — before the LLM enrichment pipeline —
    so raw data is never lost even if downstream stages fail.

    `opportunity_id` is None when the posting was a duplicate or rejected.
    Querying ScrapeResult lets us audit exactly what each scrape found.
    """

    scrape_job_id: int
    raw_url: str
    fingerprint: str

    id: int | None = None
    opportunity_id: int | None = None   # null if duplicate or rejected
    was_duplicate: bool = False
    was_rejected: bool = False
    rejection_reason: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def was_ingested(self) -> bool:
        return self.opportunity_id is not None
