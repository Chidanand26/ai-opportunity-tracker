from app.domain.ports.llm_port import LLMPort, MatchResult
from app.domain.ports.notification_repository import NotificationRepository
from app.domain.ports.notifier_port import NotifierPort
from app.domain.ports.opportunity_match_repository import OpportunityMatchRepository
from app.domain.ports.opportunity_repository import OpportunityRepository
from app.domain.ports.organization_repository import OrganizationRepository
from app.domain.ports.professor_repository import ProfessorRepository
from app.domain.ports.scrape_job_repository import ScrapeJobRepository
from app.domain.ports.scraper_port import RawPosting, SourceAdapter
from app.domain.ports.skill_repository import SkillRepository
from app.domain.ports.source_repository import SourceRepository
from app.domain.ports.user_profile_repository import UserProfileRepository

__all__ = [
    "LLMPort",
    "MatchResult",
    "NotificationRepository",
    "NotifierPort",
    "OpportunityMatchRepository",
    "OpportunityRepository",
    "OrganizationRepository",
    "ProfessorRepository",
    "RawPosting",
    "ScrapeJobRepository",
    "SkillRepository",
    "SourceAdapter",
    "SourceRepository",
    "UserProfileRepository",
]
