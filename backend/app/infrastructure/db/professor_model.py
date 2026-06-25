from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.db.opportunity_model import OpportunityModel
    from app.infrastructure.db.organization_model import OrganizationModel


class ProfessorModel(Base):
    __tablename__ = "professors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), default="")
    profile_url: Mapped[str] = mapped_column(String(500), default="")
    department: Mapped[str] = mapped_column(String(255), default="")
    lab_name: Mapped[str] = mapped_column(String(255), default="")
    research_areas: Mapped[list[str]] = mapped_column(JSONB, default=list)  # ["NLP", "CV"]
    bio: Mapped[str] = mapped_column(Text, default="")
    is_accepting_students: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    google_scholar_url: Mapped[str] = mapped_column(String(500), default="")
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)

    # Relationships
    organization: Mapped[OrganizationModel] = relationship(
        "OrganizationModel", back_populates="professors"
    )
    opportunities: Mapped[list[OpportunityModel]] = relationship(
        "OpportunityModel", back_populates="professor"
    )

    __table_args__ = (
        Index("ix_professors_organization_id", "organization_id"),
        Index("ix_professors_name", "name"),
    )
