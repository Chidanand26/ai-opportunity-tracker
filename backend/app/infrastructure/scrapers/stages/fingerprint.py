"""
FingerprintStage — compute content hash and detect duplicates.

For each NormalizedPosting:
  1. Compute Fingerprint from (title, org_name, url).
  2. Query the repository for an existing Opportunity with that fingerprint.
  3. If found: mark as_duplicate, skip persist.
  4. If not found: mark as new (is_duplicate=False).

This stage never raises — duplicates are soft-rejected (marked, not removed).
"""

from __future__ import annotations

from app.core.logging import get_logger
from app.domain.ports.opportunity_repository import OpportunityRepository
from app.domain.value_objects.fingerprint import Fingerprint
from app.infrastructure.scrapers.context import ScrapeContext

logger = get_logger(__name__)


class FingerprintStage:
    def __init__(self, opp_repo: OpportunityRepository) -> None:
        self._opp_repo = opp_repo

    async def run(self, ctx: ScrapeContext) -> ScrapeContext:
        for posting in ctx.normalized_postings:
            raw = posting.raw
            fp = Fingerprint.generate(
                title=raw.title,
                organization_name=raw.organization_name,
                url=raw.url,
            )
            posting.fingerprint = fp.value

            try:
                existing = await self._opp_repo.get_by_fingerprint(fp.value)
                if existing is not None:
                    posting.is_duplicate = True
                    ctx.metrics.postings_duplicate += 1
                    logger.debug(
                        "posting_duplicate",
                        fingerprint=fp.value,
                        title=raw.title,
                        existing_id=existing.id,
                    )
                else:
                    logger.debug("posting_new", fingerprint=fp.value, title=raw.title)
            except Exception as exc:
                # If the repo is unreachable, treat as non-duplicate (safe default)
                logger.warning(
                    "fingerprint_repo_error",
                    fingerprint=fp.value,
                    error=str(exc),
                )
                ctx.errors.append(exc)

        new_count = sum(1 for p in ctx.normalized_postings if not p.is_duplicate)
        logger.info(
            "fingerprint_stage_complete",
            total=len(ctx.normalized_postings),
            duplicates=ctx.metrics.postings_duplicate,
            new=new_count,
        )
        return ctx
