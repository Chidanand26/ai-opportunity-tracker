"""
BaseSourceAdapter — the only class concrete adapters inherit from.

Subclasses implement exactly two methods:
  • get_start_urls(source)   — which URLs to scrape
  • parse_postings(content, url, source)  — source-specific extraction

Everything else — HTTP session, retry, rate limiting, robots.txt, logging,
Playwright fallback — is provided by the base class via composition.

Example minimal adapter:

    class MyLabAdapter(BaseSourceAdapter):
        opportunity_type = OpportunityType.RA_POSITION

        async def get_start_urls(self, source: Source) -> list[str]:
            return [source.url]

        async def parse_postings(
            self, content: str, url: str, source: Source
        ) -> list[RawPosting]:
            soup = BeautifulSoup(content, "lxml")
            ...
            return [RawPosting(title=..., url=..., organization_name=...)]
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from types import TracebackType
from typing import Any, ClassVar

from app.core.logging import get_logger
from app.domain.entities.source import Source
from app.domain.enums import OpportunityType
from app.domain.ports.scraper_port import RawPosting
from app.infrastructure.scrapers.context import FetchedPage
from app.infrastructure.scrapers.exceptions import FetchError, HttpError, RobotsBlockedError
from app.infrastructure.scrapers.http_client import HttpClient
from app.infrastructure.scrapers.rate_limiter import RateLimiter
from app.infrastructure.scrapers.robots import RobotsChecker


class BaseSourceAdapter(ABC):
    """
    Abstract base for all source adapters.

    Configuration is declared as ClassVar so it is visible to both the
    instance and the pipeline without instantiation.
    """

    # ── Override these in subclasses ─────────────────────────────────────────
    opportunity_type: ClassVar[OpportunityType] = OpportunityType.RESEARCH_INTERNSHIP
    needs_browser: ClassVar[bool] = False
    requests_per_minute: ClassVar[int] = 10
    respect_robots_txt: ClassVar[bool] = True
    timeout_seconds: ClassVar[int] = 30
    user_agent: ClassVar[str] = (
        "AIOpportunityTracker/1.0 (research aggregator; "
        "contact: admin@example.com)"
    )
    # Proxy URL string — None means no proxy; override per-adapter or pass via source.config
    proxy: ClassVar[str | None] = None

    # ── Internal state (not part of public interface) ─────────────────────────
    def __init__(self, source_config: dict[str, Any] | None = None) -> None:
        """
        Args:
            source_config: The source.config dict from the database — adapter-specific
                settings (CSS selectors, auth tokens, etc.).
        """
        self._config: dict[str, Any] = source_config or {}
        self._http: HttpClient | None = None
        self._rate_limiter = RateLimiter(self.requests_per_minute)
        self._robots = RobotsChecker()
        self._logger = get_logger(self.__class__.__name__)

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    async def __aenter__(self) -> BaseSourceAdapter:
        proxy = self._config.get("proxy") or self.proxy
        self._http = HttpClient(
            user_agent=self.user_agent,
            timeout=self.timeout_seconds,
            proxy=proxy,
        )
        await self._http.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._http:
            await self._http.__aexit__(exc_type, exc_value, traceback)

    # ── Abstract interface — subclasses implement ONLY these ─────────────────

    @abstractmethod
    async def get_start_urls(self, source: Source) -> list[str]:
        """Return the list of URLs this adapter should scrape for a given source."""
        ...

    @abstractmethod
    async def parse_postings(
        self, content: str, url: str, source: Source
    ) -> list[RawPosting]:
        """
        Extract postings from fetched content.

        Args:
            content: Raw text (HTML, XML, JSON, …) from the fetched page.
            url:     URL of the page (useful for resolving relative links).
            source:  The Source entity (includes source.config).

        Returns:
            A list of RawPosting objects.  Return an empty list if no
            postings are found — do not raise.
        """
        ...

    # ── Optional overrides ────────────────────────────────────────────────────

    async def get_next_page_urls(
        self, content: str, url: str, source: Source
    ) -> list[str]:
        """Return URLs of subsequent pages (pagination).  Default: no pagination."""
        return []

    def validate_response(self, page: FetchedPage) -> bool:
        """
        Return True if the page should be parsed.
        Override to add source-specific checks (e.g. detect login-wall pages).
        Default: accept any 2xx response with non-empty content.
        """
        return page.is_ok and len(page.content.strip()) > 100

    async def is_reachable(self, source: Source) -> bool:
        """Quick connectivity check used by the admin health panel."""
        assert self._http is not None, "Call inside async context manager"
        try:
            _, status, _ = await self._http.get_text(source.url)
            return 200 <= status < 400
        except Exception:
            return False

    # ── Provided infrastructure — do NOT override in subclasses ──────────────

    async def fetch(self, url: str) -> FetchedPage:
        """
        Fetch a single URL with rate limiting, robots.txt, and retry built in.

        Raises:
            RobotsBlockedError: if robots.txt disallows the URL.
            FetchError / HttpError: on network or HTTP failures after retries.
        """
        assert self._http is not None, "Call inside async context manager"

        # 1. robots.txt check
        if self.respect_robots_txt:
            allowed = await self._robots.is_allowed(url, self._http, self.user_agent)
            if not allowed:
                raise RobotsBlockedError(url, self.user_agent)

        # 2. Per-domain rate limit
        await self._rate_limiter.acquire(url)

        # 3. Fetch (httpx or Playwright)
        self._logger.debug("fetching", url=url, needs_browser=self.needs_browser)
        try:
            if self.needs_browser:
                content = await self._fetch_with_browser(url)
                status_code, content_type = 200, "text/html"
            else:
                content, status_code, content_type = await self._http.get_text(url)
        except (FetchError, HttpError):
            raise
        except Exception as exc:
            raise FetchError(url, str(exc)) from exc

        if status_code in (403, 410):
            raise HttpError(url, status_code)

        return FetchedPage(
            url=url,
            content=content,
            status_code=status_code,
            content_type=content_type,
            fetched_at=datetime.utcnow(),
        )

    async def _fetch_with_browser(self, url: str) -> str:
        """Lazy Playwright fetch — BrowserManager is created per-call for simplicity."""
        from app.infrastructure.scrapers.browser import BrowserManager

        wait_for = self._config.get("wait_for_selector")
        async with BrowserManager(
            headless=True,
            proxy=self._config.get("proxy") or self.proxy,
            timeout_ms=self.timeout_seconds * 1000,
        ) as browser:
            return await browser.get_page_content(url, wait_for_selector=wait_for)

    async def fetch_all(self, urls: list[str]) -> list[FetchedPage]:
        """Fetch multiple URLs sequentially (rate limiting handles pacing)."""
        pages: list[FetchedPage] = []
        for url in urls:
            try:
                page = await self.fetch(url)
                pages.append(page)
            except Exception as exc:
                self._logger.warning("fetch_failed", url=url, error=str(exc))
        return pages
