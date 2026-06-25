from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.db.user_profile_model import UserProfileModel
    from app.infrastructure.db.opportunity_match_model import OpportunityMatchModel


class NotificationModel(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False
    )
    opportunity_match_id: Mapped[int | None] = mapped_column(
        ForeignKey("opportunity_matches.id", ondelete="SET NULL"), nullable=True
    )

    notification_type: Mapped[str] = mapped_column(String(50), nullable=False)
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    # Relationships
    profile: Mapped[UserProfileModel] = relationship(
        "UserProfileModel", back_populates="notifications"
    )
    opportunity_match: Mapped[OpportunityMatchModel | None] = relationship(
        "OpportunityMatchModel", back_populates="notifications"
    )

    __table_args__ = (
        Index("ix_notifications_profile_id_sent_at", "profile_id", "sent_at"),
        Index("ix_notifications_is_read", "is_read"),
    )
