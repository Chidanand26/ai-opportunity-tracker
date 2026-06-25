"""
EmitStage — finalise the ScrapeJob record and fire downstream events.

Responsibilities:
  1. Update the ScrapeJob with final metrics (found/new counts, status, timestamps).
  2. Log a structured summary for observability.
  3. Enqueue Celery enrichment tasks for newly persisted Opportunities.
     (Enrichment = LLM summarize + match-score — done async, not in this stage.)

This stage always runs — even if earlier stages had errors — so the ScrapeJob
record is always left in a terminal state (SUCCESS or FAILED).
"""

from __future__ import annotations

from datetime import datetime

from app.core.logging import get_logger
from app.domain.enums import ScrapeStatus
from app.domain.ports.scrape_job_repository import ScrapeJobRepository
from app.infrastructure.scrapers.context import ScrapeContext

logger = get_logger(__name__)


class EmitStage:
    def __init__(self, job_repo: ScrapeJobRepository) -> None:
        self._job_repo = job_repo

    async def run(self, ctx: ScrapeContext) -> ScrapeContext:
        job = ctx.job
        metrics = ctx.metrics

        # Determine final status
        if ctx.errors and not ctx.persisted_opportunities:
            job.status = ScrapeStatus.FAILED
            job.error_message = "; ".join(str(e) for e in ctx.errors[:3])
        else:
            job.status = ScrapeStatus.SUCCESS

        job.completed_at = datetime.utcnow()
        job.opportunities_found = metrics.postings_parsed
        job.opportunities_new = metrics.postings_new

        try:
            await self._job_repo.update(job)
        except Exception as exc:
            # Don't let a job-update failure mask a successful scrape
            logger.error("emit_job_update_failed", job_id=job.id, error=str(exc))

        # Structured summary — useful for dashboards and alerting
        logger.info(
            "scrape_complete",
            source_id=ctx.source.id,
            source_name=ctx.source.name,
            status=job.status,
            pages_fetched=metrics.pages_fetched,
            postings_found=metrics.postings_parsed,
            postings_new=metrics.postings_new,
            postings_duplicate=metrics.postings_duplicate,
            postings_rejected=metrics.postings_rejected,
            errors=len(ctx.errors),
            fetch_ms=round(metrics.fetch_duration_ms),
            persist_ms=round(metrics.persist_duration_ms),
        )

        # Enqueue LLM enrichment for new opportunities
        if ctx.persisted_opportunities:
            self._enqueue_enrichment(ctx)

        return ctx

    def _enqueue_enrichment(self, ctx: ScrapeContext) -> None:
        """
        Fire-and-forget Celery tasks to summarise and score each new opportunity.

        Import deferred to avoid circular dependency: workers → tasks → scrapers.
        Tasks are not yet implemented (Step 6) — this is a no-op stub.
        """
        ids = [opp.id for opp in ctx.persisted_opportunities if opp.id]
        logger.info(
            "enrichment_enqueued",
            opportunity_ids=ids,
            note="enrichment tasks are implemented in Step 6",
        )
        # TODO (Step 6): from app.workers.tasks.enrich import enrich_opportunity
        #                for opp_id in ids:
        #                    enrich_opportunity.delay(opp_id)
