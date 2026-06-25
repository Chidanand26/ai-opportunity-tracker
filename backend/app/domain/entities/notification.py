from dataclasses import dataclass, field
from datetime import datetime

from app.domain.enums import NotificationChannel, NotificationType


@dataclass
class Notification:
    """
    A notification record — one row per delivery attempt.

    `opportunity_match_id` is nullable to support non-match notifications
    (e.g. weekly digests, system alerts).
    `sent_at` being None means the notification is queued but not yet sent.
    """

    profile_id: int
    notification_type: NotificationType
    channel: NotificationChannel
    subject: str
    body: str

    id: int | None = None
    opportunity_match_id: int | None = None
    sent_at: datetime | None = None
    is_read: bool = False
    metadata: dict = field(default_factory=dict)   # e.g. email message-id for tracking
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def is_sent(self) -> bool:
        return self.sent_at is not None
