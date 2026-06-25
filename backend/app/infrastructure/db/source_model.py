from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.db.opportunity_model import OpportunityModel
    from app.infrastructure.db.organization_model import OrganizationModel
    from app.infrastructure.db.scrape_job_model import ScrapeJobModel


class SourceModel(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    adapter_class: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    scrape_frequency_hours: Mapped[int] = mapped_column(Integer, default=24, nullable=False)
    config: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    last_scraped_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    organization: Mapped[OrganizationModel | None] = relationship(
        "OrganizationModel", back_populates="sources"
    )
    opportunities: Mapped[list[OpportunityModel]] = relationship(
        "OpportunityModel", back_populates="source"
    )
    scrape_jobs: Mapped[list[ScrapeJobModel]] = relationship(
        "ScrapeJobModel", back_populates="source", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_sources_is_active", "is_active"),
        Index("ix_sources_source_type", "source_type"),
    )
