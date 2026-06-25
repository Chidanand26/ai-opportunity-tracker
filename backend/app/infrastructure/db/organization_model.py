from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.db.opportunity_model import OpportunityModel
    from app.infrastructure.db.professor_model import ProfessorModel
    from app.infrastructure.db.source_model import SourceModel


class OrganizationModel(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    org_type: Mapped[str] = mapped_column(String(50), nullable=False)
    website: Mapped[str] = mapped_column(String(500), default="")
    logo_url: Mapped[str] = mapped_column(String(500), default="")
    country: Mapped[str] = mapped_column(String(100), default="")
    city: Mapped[str] = mapped_column(String(100), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)

    # Relationships
    professors: Mapped[list[ProfessorModel]] = relationship(
        "ProfessorModel", back_populates="organization", cascade="all, delete-orphan"
    )
    sources: Mapped[list[SourceModel]] = relationship(
        "SourceModel", back_populates="organization"
    )
    opportunities: Mapped[list[OpportunityModel]] = relationship(
        "OpportunityModel", back_populates="organization"
    )

    __table_args__ = (
        Index("ix_organizations_name", "name"),
        Index("ix_organizations_org_type", "org_type"),
    )
