from sqlalchemy import select

from app.domain.entities.scrape_job import ScrapeJob
from app.domain.entities.scrape_result import ScrapeResult
from app.infrastructure.db.mappers.scrape_job_mapper import (
    apply_job_to_model,
    job_to_entity,
    job_to_model,
    result_to_entity,
    result_to_model,
)
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.scrape_job_model import ScrapeJobModel
from app.infrastructure.db.scrape_result_model import ScrapeResultModel


class SqlAlchemyScrapeJobRepository(BaseRepository):
    async def get_by_id(self, id: int) -> ScrapeJob | None:
        m = await self._session.get(ScrapeJobModel, id)
        return job_to_entity(m) if m else None

    async def save(self, job: ScrapeJob) -> ScrapeJob:
        m = job_to_model(job)
        self._session.add(m)
        await self._session.flush()
        await self._session.refresh(m)
        return job_to_entity(m)

    async def update(self, job: ScrapeJob) -> ScrapeJob:
        m = await self._session.get(ScrapeJobModel, job.id)
        if m is None:
            raise ValueError(f"ScrapeJob id={job.id} not found")
        apply_job_to_model(job, m)
        await self._session.flush()
        await self._session.refresh(m)
        return job_to_entity(m)

    async def list_recent(
        self, source_id: int | None = None, limit: int = 20
    ) -> list[ScrapeJob]:
        stmt = (
            select(ScrapeJobModel)
            .order_by(ScrapeJobModel.created_at.desc())
            .limit(limit)
        )
        if source_id is not None:
            stmt = stmt.where(ScrapeJobModel.source_id == source_id)
        result = await self._session.execute(stmt)
        return [job_to_entity(m) for m in result.scalars().all()]

    async def save_result(self, result: ScrapeResult) -> ScrapeResult:
        m = result_to_model(result)
        self._session.add(m)
        await self._session.flush()
        await self._session.refresh(m)
        return result_to_entity(m)

    async def list_results(self, job_id: int) -> list[ScrapeResult]:
        stmt = (
            select(ScrapeResultModel)
            .where(ScrapeResultModel.scrape_job_id == job_id)
            .order_by(ScrapeResultModel.created_at)
        )
        result = await self._session.execute(stmt)
        return [result_to_entity(m) for m in result.scalars().all()]
