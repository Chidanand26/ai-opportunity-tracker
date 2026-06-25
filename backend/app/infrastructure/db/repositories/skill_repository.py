from sqlalchemy import select

from app.domain.entities.skill import Skill
from app.domain.enums import SkillCategory
from app.infrastructure.db.mappers.skill_mapper import to_entity, to_model
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.skill_model import SkillModel


class SqlAlchemySkillRepository(BaseRepository):
    async def get_by_id(self, id: int) -> Skill | None:
        m = await self._session.get(SkillModel, id)
        return to_entity(m) if m else None

    async def get_by_name(self, name: str) -> Skill | None:
        stmt = select(SkillModel).where(SkillModel.name == name)
        result = await self._session.execute(stmt)
        m = result.scalar_one_or_none()
        return to_entity(m) if m else None

    async def get_or_create(self, name: str, category: SkillCategory) -> Skill:
        existing = await self.get_by_name(name)
        if existing:
            return existing
        return await self.save(Skill(name=name, category=category))

    async def save(self, skill: Skill) -> Skill:
        m = to_model(skill)
        self._session.add(m)
        await self._session.flush()
        await self._session.refresh(m)
        return to_entity(m)

    async def list_all(self) -> list[Skill]:
        stmt = select(SkillModel).order_by(SkillModel.name)
        result = await self._session.execute(stmt)
        return [to_entity(m) for m in result.scalars().all()]
