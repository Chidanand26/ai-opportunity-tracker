from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.db.source_model import SourceModel
    from app.infrastructure.db.scrape_result_model import ScrapeResultModel


class ScrapeJobModel(Base):
    __tablename__ = "scrape_jobs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"), nullable=False
    )

    celery_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    opportunities_found: Mapped[int] = mapped_column(Integer, default=0)
    opportunities_new: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    source: Mapped[SourceModel] = relationship("SourceModel", back_populates="scrape_jobs")
    results: Mapped[list[ScrapeResultModel]] = relationship(
        "ScrapeResultModel", back_populates="scrape_job", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_scrape_jobs_source_id_status", "source_id", "status"),
        Index("ix_scrape_jobs_created_at", "created_at"),
    )
