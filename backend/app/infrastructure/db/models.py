"""
ORM model registry — the single place Alembic looks to build its migration diff.

Rule: every SQLAlchemy model file MUST be imported here, or Alembic will not
detect its tables and indexes when running autogenerate.

Import order: tables with no FK dependencies first, then dependents.
"""

# Base (must be first)
from app.infrastructure.db.base import Base  # noqa: F401

# Leaf tables (no FKs to other domain tables)
from app.infrastructure.db.organization_model import OrganizationModel  # noqa: F401
from app.infrastructure.db.skill_model import SkillModel, opportunity_skills, profile_skills  # noqa: F401

# One FK level deep
from app.infrastructure.db.professor_model import ProfessorModel  # noqa: F401
from app.infrastructure.db.source_model import SourceModel  # noqa: F401
from app.infrastructure.db.user_profile_model import UserProfileModel  # noqa: F401

# Two FK levels deep
from app.infrastructure.db.opportunity_model import OpportunityModel  # noqa: F401
from app.infrastructure.db.scrape_job_model import ScrapeJobModel  # noqa: F401

# Three FK levels deep
from app.infrastructure.db.opportunity_match_model import OpportunityMatchModel  # noqa: F401
from app.infrastructure.db.scrape_result_model import ScrapeResultModel  # noqa: F401

# Four FK levels deep
from app.infrastructure.db.notification_model import NotificationModel  # noqa: F401

__all__ = [
    "Base",
    "NotificationModel",
    "OpportunityMatchModel",
    "OpportunityModel",
    "OrganizationModel",
    "ProfessorModel",
    "ScrapeJobModel",
    "ScrapeResultModel",
    "SkillModel",
    "SourceModel",
    "UserProfileModel",
    "opportunity_skills",
    "profile_skills",
]
