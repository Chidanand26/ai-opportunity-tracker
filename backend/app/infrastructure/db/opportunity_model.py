from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base
from app.infrastructure.db.skill_model import opportunity_skills

if TYPE_CHECKING:
    from app.infrastructure.db.opportunity_match_model import OpportunityMatchModel
    from app.infrastructure.db.organization_model import OrganizationModel
    from app.infrastructure.db.professor_model import ProfessorModel
    from app.infrastructure.db.scrape_result_model import ScrapeResultModel
    from app.infrastructure.db.skill_model import SkillModel
    from app.infrastructure.db.source_model import SourceModel


class OpportunityModel(Base):
    __tablename__ = "opportunities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"), nullable=False
    )
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True
    )
    professor_id: Mapped[int | None] = mapped_column(
        ForeignKey("professors.id", ondelete="SET NULL"), nullable=True
    )

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    opportunity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    summary: Mapped[str] = mapped_column(Text, default="")  # AI-generated
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    fingerprint: Mapped[str] = mapped_column(String(16), nullable=False)

    location: Mapped[str] = mapped_column(String(255), default="")
    location_type: Mapped[str] = mapped_column(String(20), default="not_specified")
    city: Mapped[str] = mapped_column(String(100), default="")
    country: Mapped[str] = mapped_column(String(100), default="")

    stipend_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    stipend_currency: Mapped[str] = mapped_column(String(3), default="USD")

    application_deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    duration_weeks: Mapped[int | None] = mapped_column(Integer, nullable=True)
    requirements: Mapped[str] = mapped_column(Text, default="")

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    raw_data: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)

    # Relationships
    source: Mapped[SourceModel] = relationship("SourceModel", back_populates="opportunities")
    organization: Mapped[OrganizationModel | None] = relationship(
        "OrganizationModel", back_populates="opportunities"
    )
    professor: Mapped[ProfessorModel | None] = relationship(
        "ProfessorModel", back_populates="opportunities"
    )
    skills: Mapped[list[SkillModel]] = relationship(
        "SkillModel", secondary=opportunity_skills, backref="opportunities"
    )
    matches: Mapped[list[OpportunityMatchModel]] = relationship(
        "OpportunityMatchModel", back_populates="opportunity", cascade="all, delete-orphan"
    )
    scrape_results: Mapped[list[ScrapeResultModel]] = relationship(
        "ScrapeResultModel", back_populates="opportunity"
    )

    __table_args__ = (
        UniqueConstraint("fingerprint", name="uq_opportunities_fingerprint"),
        Index("ix_opportunities_source_id_is_active", "source_id", "is_active"),
        Index("ix_opportunities_opportunity_type", "opportunity_type"),
        Index("ix_opportunities_application_deadline", "application_deadline"),
        Index("ix_opportunities_organization_id", "organization_id"),
    )
