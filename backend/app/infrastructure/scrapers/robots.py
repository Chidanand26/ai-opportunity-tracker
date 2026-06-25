"""
robots.txt awareness.

Fetches and caches robots.txt per domain, then checks whether a URL
is allowed for our user-agent.

Design:
- One RobotsChecker instance per BaseSourceAdapter instance.
- Cache lives in memory for the adapter's lifetime (one scrape job).
- On fetch failure (timeout, 404, etc.): fail-open — assume allowed.
  This is the correct default for a research / educational tool.
- Uses stdlib urllib.robotparser — no new dependency.
"""

from __future__ import annotations

from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

from app.core.logging import get_logger

logger = get_logger(__name__)


class RobotsChecker:
    """
    Async robots.txt checker with in-memory per-domain caching.

    Requires an HttpClient to fetch robots.txt files.
    Import HttpClient lazily to avoid circular imports.
    """

    def __init__(self) -> None:
        self._cache: dict[str, RobotFileParser] = {}

    async def is_allowed(
        self,
        url: str,
        http_client: object,   # HttpClient — typed as object to avoid circular import
        user_agent: str = "*",
    ) -> bool:
        """
        Return True if the URL is allowed to be fetched.
        Returns True (fail-open) if robots.txt is unreachable.
        """
        from app.infrastructure.scrapers.http_client import HttpClient

        assert isinstance(http_client, HttpClient)

        domain = self._get_domain(url)
        if domain not in self._cache:
            self._cache[domain] = await self._fetch_and_parse(
                domain, http_client, user_agent
            )
        return self._cache[domain].can_fetch(user_agent, url)

    @staticmethod
    def _get_domain(url: str) -> str:
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    @staticmethod
    async def _fetch_and_parse(
        domain: str,
        http_client: object,
        user_agent: str,
    ) -> RobotFileParser:
        from app.infrastructure.scrapers.http_client import HttpClient

        assert isinstance(http_client, HttpClient)

        robots_url = f"{domain}/robots.txt"
        rp = RobotFileParser()
        rp.set_url(robots_url)

        try:
            content, status, _ = await http_client.get_text(robots_url)
            if status == 200:
                rp.parse(content.splitlines())
                logger.debug("robots_fetched", domain=domain, user_agent=user_agent)
            else:
                # No robots.txt or server error — assume allowed
                logger.debug(
                    "robots_not_found", domain=domain, status=status
                )
        except Exception as exc:
            logger.warning(
                "robots_fetch_failed",
                domain=domain,
                error=str(exc),
            )
            # Fail-open: return a permissive parser
        return rp
