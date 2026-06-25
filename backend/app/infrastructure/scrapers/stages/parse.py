"""
ParseStage — delegates to adapter.parse_postings() for each valid page.

This stage is intentionally thin: it calls the adapter and aggregates results.
All source-specific intelligence lives in the adapter, not here.

Error handling: if parsing a single page raises, the error is logged and
that page is skipped. Other pages are still parsed.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.core.logging import get_logger
from app.infrastructure.scrapers.context import ScrapeContext
from app.infrastructure.scrapers.exceptions import ParseError

if TYPE_CHECKING:
    from app.infrastructure.scrapers.adapter import BaseSourceAdapter

logger = get_logger(__name__)


class ParseStage:
    def __init__(self, adapter: "BaseSourceAdapter") -> None:
        self._adapter = adapter

    async def run(self, ctx: ScrapeContext) -> ScrapeContext:
        for page in ctx.fetched_pages:
            try:
                postings = await self._adapter.parse_postings(
                    page.content, page.url, ctx.source
                )
                ctx.raw_postings.extend(postings)
                ctx.metrics.postings_parsed += len(postings)
                logger.debug(
                    "page_parsed",
                    url=page.url,
                    postings_found=len(postings),
                )
            except ParseError as exc:
                logger.warning("parse_failed", url=page.url, error=str(exc))
                ctx.errors.append(exc)
                ctx.metrics.errors += 1
            except Exception as exc:
                logger.warning(
                    "parse_unexpected_error",
                    url=page.url,
                    error=str(exc),
                )
                ctx.errors.append(exc)
                ctx.metrics.errors += 1

        logger.info(
            "parse_stage_complete",
            pages=len(ctx.fetched_pages),
            postings_parsed=ctx.metrics.postings_parsed,
        )
        return ctx
