from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.db.scrape_job_model import ScrapeJobModel
    from app.infrastructure.db.opportunity_model import OpportunityModel


class ScrapeResultModel(Base):
    __tablename__ = "scrape_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    scrape_job_id: Mapped[int] = mapped_column(
        ForeignKey("scrape_jobs.id", ondelete="CASCADE"), nullable=False
    )
    opportunity_id: Mapped[int | None] = mapped_column(
        ForeignKey("opportunities.id", ondelete="SET NULL"), nullable=True
    )

    raw_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    fingerprint: Mapped[str] = mapped_column(String(16), nullable=False)
    was_duplicate: Mapped[bool] = mapped_column(Boolean, default=False)
    was_rejected: Mapped[bool] = mapped_column(Boolean, default=False)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    scrape_job: Mapped[ScrapeJobModel] = relationship(
        "ScrapeJobModel", back_populates="results"
    )
    opportunity: Mapped[OpportunityModel | None] = relationship(
        "OpportunityModel", back_populates="scrape_results"
    )

    __table_args__ = (
        Index("ix_scrape_results_scrape_job_id", "scrape_job_id"),
        Index("ix_scrape_results_fingerprint", "fingerprint"),
    )
