from sqlalchemy import or_, select

from app.domain.entities.organization import Organization
from app.infrastructure.db.mappers.organization_mapper import (
    apply_to_model,
    to_entity,
    to_model,
)
from app.infrastructure.db.organization_model import OrganizationModel
from app.infrastructure.db.repositories.base import BaseRepository


class SqlAlchemyOrganizationRepository(BaseRepository):
    async def get_by_id(self, id: int) -> Organization | None:
        m = await self._session.get(OrganizationModel, id)
        return to_entity(m) if m else None

    async def get_by_name(self, name: str) -> Organization | None:
        stmt = select(OrganizationModel).where(OrganizationModel.name == name)
        result = await self._session.execute(stmt)
        m = result.scalar_one_or_none()
        return to_entity(m) if m else None

    async def save(self, org: Organization) -> Organization:
        m = to_model(org)
        self._session.add(m)
        await self._session.flush()
        await self._session.refresh(m)
        return to_entity(m)

    async def update(self, org: Organization) -> Organization:
        m = await self._session.get(OrganizationModel, org.id)
        if m is None:
            raise ValueError(f"Organization id={org.id} not found")
        apply_to_model(org, m)
        await self._session.flush()
        await self._session.refresh(m)
        return to_entity(m)

    async def list_all(self, limit: int = 200) -> list[Organization]:
        stmt = select(OrganizationModel).order_by(OrganizationModel.name).limit(limit)
        result = await self._session.execute(stmt)
        return [to_entity(m) for m in result.scalars().all()]

    async def search(self, query: str, limit: int = 50) -> list[Organization]:
        pattern = f"%{query}%"
        stmt = (
            select(OrganizationModel)
            .where(
                or_(
                    OrganizationModel.name.ilike(pattern),
                    OrganizationModel.description.ilike(pattern),
                )
            )
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [to_entity(m) for m in result.scalars().all()]
