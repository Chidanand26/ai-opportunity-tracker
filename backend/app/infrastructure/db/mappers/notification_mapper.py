from app.domain.entities.notification import Notification
from app.domain.enums import NotificationChannel, NotificationType
from app.infrastructure.db.notification_model import NotificationModel


def to_entity(m: NotificationModel) -> Notification:
    return Notification(
        id=m.id,
        profile_id=m.profile_id,
        notification_type=NotificationType(m.notification_type),
        channel=NotificationChannel(m.channel),
        subject=m.subject,
        body=m.body,
        opportunity_match_id=m.opportunity_match_id,
        sent_at=m.sent_at,
        is_read=m.is_read,
        metadata=dict(m.metadata_ or {}),
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


def to_model(e: Notification) -> NotificationModel:
    return NotificationModel(
        id=e.id,
        profile_id=e.profile_id,
        notification_type=str(e.notification_type),
        channel=str(e.channel),
        subject=e.subject,
        body=e.body,
        opportunity_match_id=e.opportunity_match_id,
        sent_at=e.sent_at,
        is_read=e.is_read,
        metadata_=e.metadata,
    )


def apply_to_model(e: Notification, m: NotificationModel) -> None:
    m.sent_at = e.sent_at
    m.is_read = e.is_read
    m.metadata_ = e.metadata
