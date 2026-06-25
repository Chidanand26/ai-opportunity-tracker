from app.domain.ports.llm_port import LLMPort, MatchResult
from app.domain.ports.notifier_port import NotifierPort
from app.domain.ports.opportunity_repository import OpportunityRepository
from app.domain.ports.scrape_job_repository import ScrapeJobRepository
from app.domain.ports.scraper_port import RawPosting, SourceAdapter
from app.domain.ports.source_repository import SourceRepository

__all__ = [
    "LLMPort",
    "MatchResult",
    "NotifierPort",
    "OpportunityRepository",
    "RawPosting",
    "ScrapeJobRepository",
    "SourceAdapter",
    "SourceRepository",
]
