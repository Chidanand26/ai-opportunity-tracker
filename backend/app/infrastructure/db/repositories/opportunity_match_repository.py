from sqlalchemy import and_, select

from app.domain.entities.opportunity_match import OpportunityMatch
from app.infrastructure.db.mappers.opportunity_match_mapper import (
    apply_to_model,
    to_entity,
    to_model,
)
from app.infrastructure.db.opportunity_match_model import OpportunityMatchModel
from app.infrastructure.db.repositories.base import BaseRepository


class SqlAlchemyOpportunityMatchRepository(BaseRepository):
    async def get_by_id(self, id: int) -> OpportunityMatch | None:
        m = await self._session.get(OpportunityMatchModel, id)
        return to_entity(m) if m else None

    async def get_by_profile_and_opportunity(
        self, profile_id: int, opportunity_id: int
    ) -> OpportunityMatch | None:
        stmt = select(OpportunityMatchModel).where(
            and_(
                OpportunityMatchModel.profile_id == profile_id,
                OpportunityMatchModel.opportunity_id == opportunity_id,
            )
        )
        result = await self._session.execute(stmt)
        m = result.scalar_one_or_none()
        return to_entity(m) if m else None

    async def save(self, match: OpportunityMatch) -> OpportunityMatch:
        m = to_model(match)
        self._session.add(m)
        await self._session.flush()
        await self._session.refresh(m)
        return to_entity(m)

    async def update(self, match: OpportunityMatch) -> OpportunityMatch:
        m = await self._session.get(OpportunityMatchModel, match.id)
        if m is None:
            raise ValueError(f"OpportunityMatch id={match.id} not found")
        apply_to_model(match, m)
        await self._session.flush()
        await self._session.refresh(m)
        return to_entity(m)

    async def list_by_profile(
        self,
        profile_id: int,
        min_score: int = 0,
        limit: int = 50,
        offset: int = 0,
    ) -> list[OpportunityMatch]:
        stmt = (
            select(OpportunityMatchModel)
            .where(
                and_(
                    OpportunityMatchModel.profile_id == profile_id,
                    OpportunityMatchModel.match_score >= min_score,
                )
            )
            .order_by(OpportunityMatchModel.match_score.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return [to_entity(m) for m in result.scalars().all()]

    async def list_unnotified_above_threshold(
        self, profile_id: int, min_score: int
    ) -> list[OpportunityMatch]:
        stmt = (
            select(OpportunityMatchModel)
            .where(
                and_(
                    OpportunityMatchModel.profile_id == profile_id,
                    OpportunityMatchModel.match_score >= min_score,
                    OpportunityMatchModel.is_notified.is_(False),
                )
            )
            .order_by(OpportunityMatchModel.match_score.desc())
        )
        result = await self._session.execute(stmt)
        return [to_entity(m) for m in result.scalars().all()]
