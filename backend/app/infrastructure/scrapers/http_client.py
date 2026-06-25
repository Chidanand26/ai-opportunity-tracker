"""
Managed httpx.AsyncClient with retry logic.

Handles the network layer for static / non-JS pages.
For JS-heavy pages, use BrowserManager instead.
"""

from __future__ import annotations

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.logging import get_logger

logger = get_logger(__name__)

# Retry on transient network errors only — not on HTTP 4xx/5xx
_RETRYABLE = (httpx.TimeoutException, httpx.ConnectError, httpx.RemoteProtocolError)


class HttpClient:
    """
    Thin async wrapper around httpx.AsyncClient.

    Provides:
    - Configurable User-Agent and timeouts
    - Optional proxy routing
    - Automatic retry on transient network errors (3 attempts, exp backoff)
    - Async context manager for connection-pool lifecycle

    Usage:
        async with HttpClient(user_agent="...", timeout=30) as client:
            page = await client.get("https://example.com/feed.rss")
    """

    def __init__(
        self,
        user_agent: str = "AIOpportunityTracker/1.0",
        timeout: int = 30,
        proxy: str | None = None,
    ) -> None:
        kwargs: dict = {
            "headers": {
                "User-Agent": user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            },
            "timeout": httpx.Timeout(timeout, connect=10.0),
            "follow_redirects": True,
        }
        if proxy:
            kwargs["proxy"] = proxy
        self._client = httpx.AsyncClient(**kwargs)

    async def __aenter__(self) -> "HttpClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args: object) -> None:
        await self._client.__aexit__(*args)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type(_RETRYABLE),
        reraise=True,
    )
    async def get(self, url: str, **kwargs: object) -> httpx.Response:
        """
        GET request with automatic retry on transient failures.
        Raises httpx.HTTPStatusError for non-2xx when raise_for_status=True.
        """
        logger.debug("http_get", url=url)
        response = await self._client.get(url, **kwargs)
        return response

    async def get_text(self, url: str, **kwargs: object) -> tuple[str, int, str]:
        """
        Convenience wrapper — returns (content, status_code, content_type).
        Does not raise on non-2xx; caller decides what to do with status.
        """
        resp = await self.get(url, **kwargs)
        content_type = resp.headers.get("content-type", "text/html")
        return resp.text, resp.status_code, content_type
