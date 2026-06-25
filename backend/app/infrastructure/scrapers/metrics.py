"""
Scrape metrics — accumulated as the pipeline progresses.

Attached to ScrapeContext so every stage can update it.
The EmitStage writes the final values to the ScrapeJob record.
"""

from dataclasses import dataclass, field
from time import monotonic


@dataclass
class ScrapeMetrics:
    pages_fetched: int = 0
    pages_rejected: int = 0       # failed validation
    postings_parsed: int = 0
    postings_duplicate: int = 0
    postings_rejected: int = 0    # failed normalization / quality check
    postings_new: int = 0         # successfully persisted
    fetch_duration_ms: float = 0.0
    persist_duration_ms: float = 0.0
    errors: int = 0

    # Internal timing helpers — not persisted to DB
    _fetch_start: float = field(default_factory=monotonic, repr=False)
    _persist_start: float = field(default_factory=monotonic, repr=False)

    def start_fetch(self) -> None:
        self._fetch_start = monotonic()

    def stop_fetch(self) -> None:
        self.fetch_duration_ms = (monotonic() - self._fetch_start) * 1000

    def start_persist(self) -> None:
        self._persist_start = monotonic()

    def stop_persist(self) -> None:
        self.persist_duration_ms = (monotonic() - self._persist_start) * 1000

    @property
    def total_found(self) -> int:
        return self.postings_parsed

    @property
    def dedup_rate(self) -> float:
        if self.postings_parsed == 0:
            return 0.0
        return self.postings_duplicate / self.postings_parsed
