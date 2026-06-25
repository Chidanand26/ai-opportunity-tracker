"""
FetchStage — discovers and fetches all pages for a source.

Lifecycle:
  1. Ask adapter for start URLs.
  2. Fetch each URL (rate-limited, robots-checked, retried by adapter.fetch()).
  3. For each fetched page, ask adapter for any pagination URLs and fetch those too.
  4. Append all FetchedPage objects to ctx.fetched_pages.

Error handling: if ALL URLs fail to fetch, raises to abort the pipeline.
Individual URL failures are logged and skipped.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.core.logging import get_logger
from app.infrastructure.scrapers.context import ScrapeContext
from app.infrastructure.scrapers.exceptions import FetchError

if TYPE_CHECKING:
    from app.infrastructure.scrapers.adapter import BaseSourceAdapter

logger = get_logger(__name__)


class FetchStage:
    def __init__(self, adapter: BaseSourceAdapter) -> None:
        self._adapter = adapter

    async def run(self, ctx: ScrapeContext) -> ScrapeContext:
        ctx.metrics.start_fetch()
        adapter = self._adapter
        source = ctx.source

        start_urls = await adapter.get_start_urls(source)
        logger.info(
            "fetch_stage_start",
            source_id=source.id,
            url_count=len(start_urls),
        )

        urls_to_fetch = list(start_urls)
        seen_urls: set[str] = set()

        while urls_to_fetch:
            url = urls_to_fetch.pop(0)
            if url in seen_urls:
                continue
            seen_urls.add(url)

            try:
                page = await adapter.fetch(url)
                ctx.fetched_pages.append(page)
                ctx.metrics.pages_fetched += 1

                # Pagination: ask adapter if there are more pages
                next_urls = await adapter.get_next_page_urls(
                    page.content, url, source
                )
                for next_url in next_urls:
                    if next_url not in seen_urls:
                        urls_to_fetch.append(next_url)

            except FetchError as exc:
                logger.warning(
                    "fetch_url_failed",
                    url=url,
                    error=str(exc),
                    source_id=source.id,
                )
                ctx.errors.append(exc)

        ctx.metrics.stop_fetch()

        if not ctx.fetched_pages:
            raise FetchError(source.url, "all URLs failed — aborting pipeline")

        logger.info(
            "fetch_stage_complete",
            pages_fetched=ctx.metrics.pages_fetched,
            duration_ms=round(ctx.metrics.fetch_duration_ms),
        )
        return ctx
