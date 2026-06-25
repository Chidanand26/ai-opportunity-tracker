from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.domain.enums import SourceType


@dataclass
class Source:
    """
    A monitored URL that the scraping pipeline checks for new opportunities.

    `adapter_class` is the dotted Python import path to the SourceAdapter
    implementation (e.g. "app.infrastructure.scrapers.sources.mit.MITSource").
    `config` stores adapter-specific settings (CSS selectors, auth tokens, etc.)
    in a flexible JSONB field so each adapter can define its own schema.
    """

    name: str
    url: str
    source_type: SourceType
    adapter_class: str              # dotted Python import path

    id: int | None = None
    organization_id: int | None = None  # nullable — some sources aren't org-specific
    is_active: bool = True
    scrape_frequency_hours: int = 24
    config: dict[str, Any] = field(default_factory=dict)
    last_scraped_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def is_due_for_scrape(self, now: datetime) -> bool:
        if self.last_scraped_at is None:
            return True
        from datetime import timedelta
        return now >= self.last_scraped_at + timedelta(hours=self.scrape_frequency_hours)
