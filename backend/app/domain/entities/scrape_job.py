from dataclasses import dataclass
from datetime import datetime

from app.domain.enums import ScrapeStatus


@dataclass
class ScrapeJob:
    """
    One execution of the scraping pipeline for a single Source.

    `celery_task_id` links this record to a Celery task so we can cancel,
    monitor, or retry it via the Celery API.

    `opportunities_found` = total postings seen in this run.
    `opportunities_new`   = postings not previously in the database.
    The difference = duplicates caught by the dedup stage.
    """

    source_id: int
    status: ScrapeStatus = ScrapeStatus.PENDING

    id: int | None = None
    celery_task_id: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    opportunities_found: int = 0
    opportunities_new: int = 0
    error_message: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def duration_seconds(self) -> float | None:
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def is_running(self) -> bool:
        return self.status == ScrapeStatus.RUNNING
