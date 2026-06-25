"""
ORM model registry.

Import ALL SQLAlchemy models here so that:
1. Alembic autogenerate can see every table.
2. There is one place to audit the full schema.

Models are implemented in feature-specific files and re-exported here.
"""

# Base must be imported first
from app.infrastructure.db.base import Base  # noqa: F401

# Feature models are imported here as they are added in later steps:
# from app.infrastructure.db.opportunity_model import OpportunityModel  # Step 4
# from app.infrastructure.db.source_model import SourceModel            # Step 4
# from app.infrastructure.db.profile_model import ProfileModel          # Step 4

__all__ = ["Base"]
