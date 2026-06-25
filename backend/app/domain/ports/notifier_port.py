from typing import Protocol

from app.domain.entities.notification import Notification


class NotifierPort(Protocol):
    """
    Abstract notification delivery channel.

    Implementations: SMTP adapter, SendGrid adapter (in infrastructure/notifications/).
    Additional channels (Slack, webhook) are added without touching this interface.
    """

    async def send(self, notification: Notification) -> None:
        """Deliver the notification. Raises on failure (caller handles retry)."""
        ...

    async def send_bulk(self, notifications: list[Notification]) -> list[Notification]:
        """Deliver multiple notifications; return those that succeeded."""
        ...
