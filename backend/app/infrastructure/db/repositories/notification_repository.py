from sqlalchemy import select, update

from app.domain.entities.notification import Notification
from app.infrastructure.db.mappers.notification_mapper import to_entity, to_model
from app.infrastructure.db.notification_model import NotificationModel
from app.infrastructure.db.repositories.base import BaseRepository


class SqlAlchemyNotificationRepository(BaseRepository):
    async def get_by_id(self, id: int) -> Notification | None:
        m = await self._session.get(NotificationModel, id)
        return to_entity(m) if m else None

    async def save(self, notification: Notification) -> Notification:
        m = to_model(notification)
        self._session.add(m)
        await self._session.flush()
        await self._session.refresh(m)
        return to_entity(m)

    async def list_by_profile(self, profile_id: int, limit: int = 50) -> list[Notification]:
        stmt = (
            select(NotificationModel)
            .where(NotificationModel.profile_id == profile_id)
            .order_by(NotificationModel.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [to_entity(m) for m in result.scalars().all()]

    async def mark_read(self, notification_id: int) -> None:
        stmt = (
            update(NotificationModel)
            .where(NotificationModel.id == notification_id)
            .values(is_read=True)
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def list_unsent(self) -> list[Notification]:
        stmt = (
            select(NotificationModel)
            .where(NotificationModel.sent_at.is_(None))
            .order_by(NotificationModel.created_at)
        )
        result = await self._session.execute(stmt)
        return [to_entity(m) for m in result.scalars().all()]
