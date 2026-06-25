"""
Scraping framework — public API.

Import these to use the framework:
    from app.infrastructure.scrapers import BaseSourceAdapter, ScrapePipeline
    from app.infrastructure.scrapers import RssFeedAdapter
    from app.infrastructure.scrapers.context import ScrapeContext, FetchedPage, NormalizedPosting
    from app.infrastructure.scrapers.registry import make_adapter
"""

from app.infrastructure.scrapers.adapter import BaseSourceAdapter
from app.infrastructure.scrapers.context import FetchedPage, NormalizedPosting, ScrapeContext
from app.infrastructure.scrapers.exceptions import (
    FetchError,
    HttpError,
    ParseError,
    RobotsBlockedError,
    ScraperError,
    ValidationError,
)
from app.infrastructure.scrapers.pipeline import ScrapePipeline
from app.infrastructure.scrapers.registry import get_adapter_class, make_adapter
from app.infrastructure.scrapers.sources.rss_feed import RssFeedAdapter

__all__ = [
    "BaseSourceAdapter",
    "FetchError",
    "FetchedPage",
    "HttpError",
    "NormalizedPosting",
    "ParseError",
    "RobotsBlockedError",
    "RssFeedAdapter",
    "ScrapeContext",
    "ScrapePipeline",
    "ScraperError",
    "ValidationError",
    "get_adapter_class",
    "make_adapter",
]
