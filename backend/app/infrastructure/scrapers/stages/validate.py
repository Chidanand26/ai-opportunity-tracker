"""
ValidateStage — filters out fetched pages that shouldn't be parsed.

Checks:
  1. HTTP status code is 2xx.
  2. Content is not suspiciously short (likely an error page or login wall).
  3. adapter.validate_response() passes (adapter-specific custom logic).

Pages that fail are removed from ctx.fetched_pages.
The stage never raises — bad pages are logged and counted.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.core.logging import get_logger
from app.infrastructure.scrapers.context import FetchedPage, ScrapeContext

if TYPE_CHECKING:
    from app.infrastructure.scrapers.adapter import BaseSourceAdapter

logger = get_logger(__name__)

_MIN_CONTENT_LENGTH = 200  # bytes — anything shorter is likely an error page


class ValidateStage:
    def __init__(self, adapter: BaseSourceAdapter) -> None:
        self._adapter = adapter

    async def run(self, ctx: ScrapeContext) -> ScrapeContext:
        valid: list[FetchedPage] = []

        for page in ctx.fetched_pages:
            reason = self._check(page)
            if reason:
                logger.warning(
                    "page_rejected",
                    url=page.url,
                    status=page.status_code,
                    reason=reason,
                )
                ctx.metrics.pages_rejected += 1
            elif not self._adapter.validate_response(page):
                logger.warning(
                    "page_rejected_by_adapter",
                    url=page.url,
                    status=page.status_code,
                )
                ctx.metrics.pages_rejected += 1
            else:
                valid.append(page)

        ctx.fetched_pages = valid
        return ctx

    @staticmethod
    def _check(page: FetchedPage) -> str | None:
        """Return a rejection reason string, or None if the page passes."""
        if not page.is_ok:
            return f"non-2xx status {page.status_code}"
        if len(page.content.strip()) < _MIN_CONTENT_LENGTH:
            return f"content too short ({len(page.content)} chars)"
        return None
