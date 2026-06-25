from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.db.user_profile_model import UserProfileModel
    from app.infrastructure.db.opportunity_model import OpportunityModel
    from app.infrastructure.db.notification_model import NotificationModel


class OpportunityMatchModel(Base):
    __tablename__ = "opportunity_matches"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False
    )
    opportunity_id: Mapped[int] = mapped_column(
        ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False
    )

    match_score: Mapped[int] = mapped_column(Integer, nullable=False)   # 0-100
    match_rationale: Mapped[str] = mapped_column(Text, default="")

    is_saved: Mapped[bool] = mapped_column(Boolean, default=False)
    is_applied: Mapped[bool] = mapped_column(Boolean, default=False)
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    application_notes: Mapped[str] = mapped_column(Text, default="")

    is_notified: Mapped[bool] = mapped_column(Boolean, default=False)
    notified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    profile: Mapped[UserProfileModel] = relationship(
        "UserProfileModel", back_populates="matches"
    )
    opportunity: Mapped[OpportunityModel] = relationship(
        "OpportunityModel", back_populates="matches"
    )
    notifications: Mapped[list[NotificationModel]] = relationship(
        "NotificationModel", back_populates="opportunity_match"
    )

    __table_args__ = (
        UniqueConstraint("profile_id", "opportunity_id", name="uq_match_profile_opportunity"),
        Index("ix_matches_profile_id_score", "profile_id", "match_score"),
        Index("ix_matches_is_saved", "is_saved"),
        Index("ix_matches_is_applied", "is_applied"),
    )
