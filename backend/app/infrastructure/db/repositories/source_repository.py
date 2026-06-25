from datetime import datetime

from sqlalchemy import select, update

from app.domain.entities.source import Source
from app.infrastructure.db.mappers.source_mapper import apply_to_model, to_entity, to_model
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.source_model import SourceModel


class SqlAlchemySourceRepository(BaseRepository):
    async def get_by_id(self, id: int) -> Source | None:
        m = await self._session.get(SourceModel, id)
        return to_entity(m) if m else None

    async def get_all_active(self) -> list[Source]:
        stmt = select(SourceModel).where(SourceModel.is_active.is_(True))
        result = await self._session.execute(stmt)
        return [to_entity(m) for m in result.scalars().all()]

    async def get_due_for_scrape(self) -> list[Source]:
        # Fetch all active sources and filter in Python using domain logic.
        # The Source.is_due_for_scrape() method encapsulates the schedule rule,
        # keeping the business rule in the domain rather than in SQL.
        now = datetime.utcnow()
        sources = await self.get_all_active()
        return [s for s in sources if s.is_due_for_scrape(now)]

    async def save(self, source: Source) -> Source:
        m = to_model(source)
        self._session.add(m)
        await self._session.flush()
        await self._session.refresh(m)
        return to_entity(m)

    async def update(self, source: Source) -> Source:
        m = await self._session.get(SourceModel, source.id)
        if m is None:
            raise ValueError(f"Source id={source.id} not found")
        apply_to_model(source, m)
        await self._session.flush()
        await self._session.refresh(m)
        return to_entity(m)

    async def touch_last_scraped(self, source_id: int) -> None:
        stmt = (
            update(SourceModel)
            .where(SourceModel.id == source_id)
            .values(last_scraped_at=datetime.utcnow())
        )
        await self._session.execute(stmt)
        await self._session.flush()
