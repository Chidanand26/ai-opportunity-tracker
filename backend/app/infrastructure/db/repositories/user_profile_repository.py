from sqlalchemy import select

from app.domain.entities.user_profile import UserProfile
from app.infrastructure.db.mappers.user_profile_mapper import apply_to_model, to_entity, to_model
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.user_profile_model import UserProfileModel


class SqlAlchemyUserProfileRepository(BaseRepository):
    async def get_by_id(self, id: int) -> UserProfile | None:
        m = await self._session.get(UserProfileModel, id)
        return to_entity(m) if m else None

    async def get_by_user_id(self, user_id: int) -> UserProfile | None:
        stmt = select(UserProfileModel).where(UserProfileModel.user_id == user_id)
        result = await self._session.execute(stmt)
        m = result.scalar_one_or_none()
        return to_entity(m) if m else None

    async def save(self, profile: UserProfile) -> UserProfile:
        m = to_model(profile)
        self._session.add(m)
        await self._session.flush()
        await self._session.refresh(m)
        return to_entity(m)

    async def update(self, profile: UserProfile) -> UserProfile:
        m = await self._session.get(UserProfileModel, profile.id)
        if m is None:
            raise ValueError(f"UserProfile id={profile.id} not found")
        apply_to_model(profile, m)
        await self._session.flush()
        await self._session.refresh(m)
        return to_entity(m)
