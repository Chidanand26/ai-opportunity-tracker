"""
Mapper package — domain entity ↔ SQLAlchemy ORM model conversions.

Each sub-module exposes:
  to_entity(model)          → domain entity
  to_model(entity)          → ORM model
  apply_to_model(entity, m) → update existing ORM model in-place (for UPDATE queries)

Import sub-modules by name:
    from app.infrastructure.db.mappers import opportunity_mapper
    opp = opportunity_mapper.to_entity(row)
"""

from app.infrastructure.db.mappers import (
    notification_mapper,
    opportunity_mapper,
    opportunity_match_mapper,
    organization_mapper,
    professor_mapper,
    scrape_job_mapper,
    skill_mapper,
    source_mapper,
    user_profile_mapper,
)

__all__ = [
    "notification_mapper",
    "opportunity_mapper",
    "opportunity_match_mapper",
    "organization_mapper",
    "professor_mapper",
    "scrape_job_mapper",
    "skill_mapper",
    "source_mapper",
    "user_profile_mapper",
]
