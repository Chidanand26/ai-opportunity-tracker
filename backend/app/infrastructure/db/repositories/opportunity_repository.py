from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.sql.elements import ColumnElement

from app.domain.entities.opportunity import Opportunity
from app.domain.enums import OpportunityType
from app.infrastructure.db.mappers.opportunity_mapper import apply_to_model, to_entity, to_model
from app.infrastructure.db.opportunity_model import OpportunityModel
from app.infrastructure.db.repositories.base import BaseRepository


class SqlAlchemyOpportunityRepository(BaseRepository):
    async def get_by_id(self, id: int) -> Opportunity | None:
        m = await self._session.get(OpportunityModel, id)
        return to_entity(m) if m else None

    async def get_by_fingerprint(self, fingerprint: str) -> Opportunity | None:
        stmt = select(OpportunityModel).where(OpportunityModel.fingerprint == fingerprint)
        result = await self._session.execute(stmt)
        m = result.scalar_one_or_none()
        return to_entity(m) if m else None

    async def save(self, opportunity: Opportunity) -> Opportunity:
        m = to_model(opportunity)
        self._session.add(m)
        await self._session.flush()
        await self._session.refresh(m)
        return to_entity(m)

    async def update(self, opportunity: Opportunity) -> Opportunity:
        m = await self._session.get(OpportunityModel, opportunity.id)
        if m is None:
            raise ValueError(f"Opportunity id={opportunity.id} not found")
        apply_to_model(opportunity, m)
        await self._session.flush()
        await self._session.refresh(m)
        return to_entity(m)

    async def list_active(
        self,
        limit: int = 50,
        offset: int = 0,
        opportunity_type: OpportunityType | None = None,
        organization_id: int | None = None,
    ) -> list[Opportunity]:
        stmt = (
            select(OpportunityModel)
            .where(OpportunityModel.is_active.is_(True))
            .order_by(OpportunityModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if opportunity_type is not None:
            stmt = stmt.where(OpportunityModel.opportunity_type == str(opportunity_type))
        if organization_id is not None:
            stmt = stmt.where(OpportunityModel.organization_id == organization_id)
        result = await self._session.execute(stmt)
        return [to_entity(m) for m in result.scalars().all()]

    async def search(self, query: str, limit: int = 50) -> list[Opportunity]:
        pattern = f"%{query}%"
        stmt = (
            select(OpportunityModel)
            .where(
                and_(
                    OpportunityModel.is_active.is_(True),
                    or_(
                        OpportunityModel.title.ilike(pattern),
                        OpportunityModel.description.ilike(pattern),
                        OpportunityModel.requirements.ilike(pattern),
                    ),
                )
            )
            .order_by(OpportunityModel.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [to_entity(m) for m in result.scalars().all()]

    async def count_active(
        self,
        opportunity_type: OpportunityType | None = None,
        organization_id: int | None = None,
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(OpportunityModel)
            .where(OpportunityModel.is_active.is_(True))
        )
        if opportunity_type is not None:
            stmt = stmt.where(OpportunityModel.opportunity_type == str(opportunity_type))
        if organization_id is not None:
            stmt = stmt.where(OpportunityModel.organization_id == organization_id)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def mark_inactive_by_source(self, source_id: int, except_ids: list[int]) -> int:
        conditions: list[ColumnElement[bool]] = [
            OpportunityModel.source_id == source_id,
            OpportunityModel.is_active.is_(True),
        ]
        if except_ids:
            conditions.append(OpportunityModel.id.notin_(except_ids))
        stmt = update(OpportunityModel).where(and_(*conditions)).values(is_active=False)
        result = await self._session.execute(stmt)
        await self._session.flush()
        assert isinstance(result, CursorResult)
        return result.rowcount
