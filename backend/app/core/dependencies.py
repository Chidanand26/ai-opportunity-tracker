"""
FastAPI dependency functions — resolve domain repository interfaces to their
SQLAlchemy implementations.

Usage in a router:
    from app.core.dependencies import get_opportunity_repo
    from app.domain.ports import OpportunityRepository

    @router.get("/opportunities")
    async def list_opportunities(
        repo: OpportunityRepository = Depends(get_opportunity_repo),
    ):
        return await repo.list_active()

The return type annotation uses the Protocol (port), not the concrete class,
so the router is decoupled from the infrastructure implementation.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.repositories.notification_repository import (
    SqlAlchemyNotificationRepository,
)
from app.infrastructure.db.repositories.opportunity_match_repository import (
    SqlAlchemyOpportunityMatchRepository,
)
from app.infrastructure.db.repositories.opportunity_repository import (
    SqlAlchemyOpportunityRepository,
)
from app.infrastructure.db.repositories.organization_repository import (
    SqlAlchemyOrganizationRepository,
)
from app.infrastructure.db.repositories.professor_repository import (
    SqlAlchemyProfessorRepository,
)
from app.infrastructure.db.repositories.scrape_job_repository import (
    SqlAlchemyScrapeJobRepository,
)
from app.infrastructure.db.repositories.skill_repository import SqlAlchemySkillRepository
from app.infrastructure.db.repositories.source_repository import SqlAlchemySourceRepository
from app.infrastructure.db.repositories.user_profile_repository import (
    SqlAlchemyUserProfileRepository,
)
from app.infrastructure.db.session import get_db


def get_opportunity_repo(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> SqlAlchemyOpportunityRepository:
    return SqlAlchemyOpportunityRepository(session)


def get_source_repo(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> SqlAlchemySourceRepository:
    return SqlAlchemySourceRepository(session)


def get_scrape_job_repo(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> SqlAlchemyScrapeJobRepository:
    return SqlAlchemyScrapeJobRepository(session)


def get_organization_repo(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> SqlAlchemyOrganizationRepository:
    return SqlAlchemyOrganizationRepository(session)


def get_professor_repo(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> SqlAlchemyProfessorRepository:
    return SqlAlchemyProfessorRepository(session)


def get_user_profile_repo(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> SqlAlchemyUserProfileRepository:
    return SqlAlchemyUserProfileRepository(session)


def get_skill_repo(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> SqlAlchemySkillRepository:
    return SqlAlchemySkillRepository(session)


def get_opportunity_match_repo(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> SqlAlchemyOpportunityMatchRepository:
    return SqlAlchemyOpportunityMatchRepository(session)


def get_notification_repo(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> SqlAlchemyNotificationRepository:
    return SqlAlchemyNotificationRepository(session)
