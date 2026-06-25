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

__all__ = [
    "SqlAlchemyNotificationRepository",
    "SqlAlchemyOpportunityMatchRepository",
    "SqlAlchemyOpportunityRepository",
    "SqlAlchemyOrganizationRepository",
    "SqlAlchemyProfessorRepository",
    "SqlAlchemyScrapeJobRepository",
    "SqlAlchemySkillRepository",
    "SqlAlchemySourceRepository",
    "SqlAlchemyUserProfileRepository",
]
