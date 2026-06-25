from sqlalchemy import select

from app.domain.entities.professor import Professor
from app.infrastructure.db.mappers.professor_mapper import apply_to_model, to_entity, to_model
from app.infrastructure.db.professor_model import ProfessorModel
from app.infrastructure.db.repositories.base import BaseRepository


class SqlAlchemyProfessorRepository(BaseRepository):
    async def get_by_id(self, id: int) -> Professor | None:
        m = await self._session.get(ProfessorModel, id)
        return to_entity(m) if m else None

    async def get_by_organization(self, organization_id: int) -> list[Professor]:
        stmt = (
            select(ProfessorModel)
            .where(ProfessorModel.organization_id == organization_id)
            .order_by(ProfessorModel.name)
        )
        result = await self._session.execute(stmt)
        return [to_entity(m) for m in result.scalars().all()]

    async def save(self, professor: Professor) -> Professor:
        m = to_model(professor)
        self._session.add(m)
        await self._session.flush()
        await self._session.refresh(m)
        return to_entity(m)

    async def update(self, professor: Professor) -> Professor:
        m = await self._session.get(ProfessorModel, professor.id)
        if m is None:
            raise ValueError(f"Professor id={professor.id} not found")
        apply_to_model(professor, m)
        await self._session.flush()
        await self._session.refresh(m)
        return to_entity(m)

    async def list_accepting_students(self) -> list[Professor]:
        stmt = (
            select(ProfessorModel)
            .where(ProfessorModel.is_accepting_students.is_(True))
            .order_by(ProfessorModel.name)
        )
        result = await self._session.execute(stmt)
        return [to_entity(m) for m in result.scalars().all()]
