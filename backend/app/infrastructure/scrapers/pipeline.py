"""
ScrapePipeline — chains the 7 lifecycle stages for a single source run.

Usage:
    pipeline = ScrapePipeline(opp_repo=..., job_repo=...)

    async with MyAdapter(source.config) as adapter:
        ctx = await pipeline.run(adapter, source, job)

    print(f"New: {ctx.metrics.postings_new}, Dupes: {ctx.metrics.postings_duplicate}")

Stages are constructed fresh per run so there is no shared state between runs.
"""

from __future__ import annotations

from datetime import datetime

from app.core.logging import get_logger
from app.domain.entities.scrape_job import ScrapeJob
from app.domain.entities.source import Source
from app.domain.enums import ScrapeStatus
from app.domain.ports.opportunity_repository import OpportunityRepository
from app.domain.ports.scrape_job_repository import ScrapeJobRepository
from app.infrastructure.scrapers.adapter import BaseSourceAdapter
from app.infrastructure.scrapers.context import PipelineStage, ScrapeContext
from app.infrastructure.scrapers.exceptions import FetchError
from app.infrastructure.scrapers.stages import (
    EmitStage,
    FetchStage,
    FingerprintStage,
    NormalizeStage,
    ParseStage,
    PersistStage,
    ValidateStage,
)

logger = get_logger(__name__)


class ScrapePipeline:
    """
    Orchestrates the full scraping lifecycle.

    Injects repositories into stages that need them.
    Stages that need only the adapter are passed it directly.
    """

    def __init__(
        self,
        opp_repo: OpportunityRepository,
        job_repo: ScrapeJobRepository,
    ) -> None:
        self._opp_repo = opp_repo
        self._job_repo = job_repo

    async def run(
        self,
        adapter: BaseSourceAdapter,
        source: Source,
        job: ScrapeJob,
    ) -> ScrapeContext:
        """
        Execute all 7 stages in order.

        The pipeline:
          Fetch → Validate → Parse → Normalize → Fingerprint → Persist → Emit

        EmitStage always runs so the ScrapeJob is left in a terminal state.
        If FetchStage raises (all URLs unreachable), remaining stages are skipped
        but EmitStage still marks the job as FAILED.
        """
        ctx = ScrapeContext(source=source, job=job)

        # Mark job as running before any network activity
        job.status = ScrapeStatus.RUNNING
        job.started_at = datetime.utcnow()
        try:
            await self._job_repo.update(job)
        except Exception as exc:
            logger.warning("job_update_failed", job_id=job.id, error=str(exc))

        stages_before_emit: list[PipelineStage] = [
            FetchStage(adapter),
            ValidateStage(adapter),
            ParseStage(adapter),
            NormalizeStage(adapter.opportunity_type),
            FingerprintStage(self._opp_repo),
            PersistStage(self._opp_repo, self._job_repo),
        ]
        emit_stage = EmitStage(self._job_repo)

        bound_log = logger.bind(
            source_id=source.id,
            source_name=source.name,
            adapter=type(adapter).__name__,
        )
        bound_log.info("pipeline_start")

        try:
            for stage in stages_before_emit:
                ctx = await stage.run(ctx)
                bound_log.debug(
                    "stage_ok",
                    stage=type(stage).__name__,
                    errors_so_far=len(ctx.errors),
                )
        except FetchError as exc:
            # Unrecoverable — no pages fetched; let EmitStage record the failure
            bound_log.error("pipeline_fetch_aborted", error=str(exc))
            ctx.errors.append(exc)
            ctx.job.error_message = str(exc)
        except Exception as exc:
            bound_log.error("pipeline_stage_error", error=str(exc))
            ctx.errors.append(exc)

        # EmitStage always runs regardless of earlier failures
        ctx = await emit_stage.run(ctx)
        bound_log.info("pipeline_complete", status=ctx.job.status)

        return ctx
