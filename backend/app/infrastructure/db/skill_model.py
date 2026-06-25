from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Index, String, Table, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base

# ── Association tables ────────────────────────────────────────────────────────

# Pure junction (no extra columns) — uses simple Table, not a full model
opportunity_skills = Table(
    "opportunity_skills",
    Base.metadata,
    Column("opportunity_id", ForeignKey("opportunities.id", ondelete="CASCADE"), primary_key=True),
    Column("skill_id", ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
)

# Has an extra column (proficiency_level) so it needs a full mapped class
profile_skills = Table(
    "profile_skills",
    Base.metadata,
    Column("profile_id", ForeignKey("user_profiles.id", ondelete="CASCADE"), primary_key=True),
    Column("skill_id", ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
    Column("proficiency_level", String(20), nullable=False, default="intermediate"),
)


class SkillModel(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    aliases: Mapped[list[str]] = mapped_column(JSONB, default=list)  # ["ML", "machine-learning"]

    __table_args__ = (
        UniqueConstraint("name", name="uq_skills_name"),
        Index("ix_skills_category", "category"),
    )
