"""
PersistStage — save new Opportunities and ScrapeResult records.

For each NormalizedPosting:
  - If is_duplicate: save a ScrapeResult with was_duplicate=True, opportunity_id=None.
  - If is_rejected: save a ScrapeResult with was_rejected=True.
  - Otherwise: create an Opportunity, save it, then save a ScrapeResult linking the two.

Raw data is always persisted (in Opportunity.raw_data) so re-parsing is possible
without re-scraping.

Failures on individual postings are logged and skipped (not fatal).
"""

from __future__ import annotations

from app.core.logging import get_logger
from app.domain.entities.opportunity import Opportunity
from app.domain.entities.scrape_result import ScrapeResult
from app.domain.ports.opportunity_repository import OpportunityRepository
from app.domain.ports.scrape_job_repository import ScrapeJobRepository
from app.infrastructure.scrapers.context import NormalizedPosting, ScrapeContext

logger = get_logger(__name__)


def _to_opportunity(posting: NormalizedPosting, source_id: int) -> Opportunity:
    raw = posting.raw
    return Opportunity(
        title=raw.title,
        opportunity_type=posting.opportunity_type,
        source_id=source_id,
        url=raw.url,
        fingerprint=posting.fingerprint,
        organization_id=None,    # resolved later via org lookup / enrichment
        description=raw.description,
        location=raw.location.display(),
        location_type=posting.location.location_type,
        city=posting.location.city,
        country=posting.location.country,
        stipend_amount=posting.stipend_amount,
        stipend_currency=posting.stipend_currency,
        application_deadline=posting.parsed_deadline,
        start_date=posting.parsed_start_date,
        requirements=raw.requirements,
        raw_data={
            "html": raw.raw_html[:50_000] if raw.raw_html else "",  # cap stored HTML
            **raw.extra,
        },
    )


class PersistStage:
    def __init__(
        self,
        opp_repo: OpportunityRepository,
        job_repo: ScrapeJobRepository,
    ) -> None:
        self._opp_repo = opp_repo
        self._job_repo = job_repo

    async def run(self, ctx: ScrapeContext) -> ScrapeContext:
        ctx.metrics.start_persist()
        job_id = ctx.job.id
        source_id = ctx.source.id or 0

        for posting in ctx.normalized_postings:
            try:
                await self._persist_one(posting, job_id, source_id, ctx)
            except Exception as exc:
                logger.error(
                    "persist_failed",
                    url=posting.raw.url,
                    fingerprint=posting.fingerprint,
                    error=str(exc),
                )
                ctx.errors.append(exc)
                ctx.metrics.errors += 1

        ctx.metrics.stop_persist()
        logger.info(
            "persist_stage_complete",
            new=ctx.metrics.postings_new,
            duplicates=ctx.metrics.postings_duplicate,
            duration_ms=round(ctx.metrics.persist_duration_ms),
        )
        return ctx

    async def _persist_one(
        self,
        posting: NormalizedPosting,
        job_id: int | None,
        source_id: int,
        ctx: ScrapeContext,
    ) -> None:
        if posting.is_duplicate:
            # Record the dedup without creating an Opportunity
            if job_id:
                result = ScrapeResult(
                    scrape_job_id=job_id,
                    raw_url=posting.raw.url,
                    fingerprint=posting.fingerprint,
                    was_duplicate=True,
                )
                await self._job_repo.save_result(result)
            return

        if posting.is_rejected:
            if job_id:
                result = ScrapeResult(
                    scrape_job_id=job_id,
                    raw_url=posting.raw.url,
                    fingerprint=posting.fingerprint,
                    was_rejected=True,
                    rejection_reason=posting.rejection_reason,
                )
                await self._job_repo.save_result(result)
            ctx.metrics.postings_rejected += 1
            return

        # New posting — save Opportunity then link via ScrapeResult
        opp = _to_opportunity(posting, source_id)
        saved = await self._opp_repo.save(opp)
        ctx.persisted_opportunities.append(saved)
        ctx.metrics.postings_new += 1

        if job_id:
            result = ScrapeResult(
                scrape_job_id=job_id,
                raw_url=posting.raw.url,
                fingerprint=posting.fingerprint,
                opportunity_id=saved.id,
            )
            await self._job_repo.save_result(result)
