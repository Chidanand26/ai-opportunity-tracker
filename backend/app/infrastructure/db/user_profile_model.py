from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Float, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base
from app.infrastructure.db.skill_model import profile_skills

if TYPE_CHECKING:
    from app.infrastructure.db.notification_model import NotificationModel
    from app.infrastructure.db.opportunity_match_model import OpportunityMatchModel
    from app.infrastructure.db.skill_model import SkillModel


class UserProfileModel(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # FK to future users table — always 1 in single-user MVP.
    # Add UniqueConstraint on user_id when auth is introduced.
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    bio: Mapped[str] = mapped_column(Text, default="")
    degree_level: Mapped[str] = mapped_column(String(20), default="masters")
    graduation_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gpa: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_institution: Mapped[str] = mapped_column(String(255), default="")
    research_interests: Mapped[str] = mapped_column(Text, default="")
    cv_url: Mapped[str] = mapped_column(String(500), default="")
    linkedin_url: Mapped[str] = mapped_column(String(500), default="")
    github_url: Mapped[str] = mapped_column(String(500), default="")

    # Matching preferences (drive the pre-filter stage — no LLM call)
    preferred_locations: Mapped[list[str]] = mapped_column(JSONB, default=list)
    preferred_opportunity_types: Mapped[list[str]] = mapped_column(JSONB, default=list)
    min_stipend_usd: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Notification preferences
    notification_email_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    notification_frequency: Mapped[str] = mapped_column(String(20), default="daily_digest")
    min_match_score_for_email: Mapped[int] = mapped_column(Integer, default=70)

    # Relationships
    skills: Mapped[list[SkillModel]] = relationship(
        "SkillModel", secondary=profile_skills, backref="user_profiles"
    )
    matches: Mapped[list[OpportunityMatchModel]] = relationship(
        "OpportunityMatchModel", back_populates="profile", cascade="all, delete-orphan"
    )
    notifications: Mapped[list[NotificationModel]] = relationship(
        "NotificationModel", back_populates="profile", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_user_profiles_user_id", "user_id"),
        UniqueConstraint("email", name="uq_user_profiles_email"),
    )
