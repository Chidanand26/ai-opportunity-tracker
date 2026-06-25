"""
Playwright BrowserManager — for JS-heavy or auth-gated pages.

Used by FetchStage when adapter.needs_browser == True.

Prerequisites:
    make playwright-install    # installs Chromium + system deps inside Docker
"""

from __future__ import annotations

from types import TracebackType
from typing import Any

from app.core.logging import get_logger

logger = get_logger(__name__)

_DEFAULT_TIMEOUT_MS = 30_000  # 30s
_WAIT_UNTIL = "networkidle"


class BrowserManager:
    """
    Async context manager that owns a Playwright Chromium instance.

    Usage:
        async with BrowserManager(headless=True) as browser:
            html = await browser.get_page_content("https://example.com")

    One BrowserManager per scrape job (opened in FetchStage, closed after).
    Proxy support: pass the proxy URL string (e.g. "http://user:pass@host:port").
    """

    def __init__(
        self,
        headless: bool = True,
        proxy: str | None = None,
        timeout_ms: int = _DEFAULT_TIMEOUT_MS,
    ) -> None:
        self._headless = headless
        self._proxy = proxy
        self._timeout_ms = timeout_ms
        # Typed as Any: the concrete Playwright/Browser types are imported lazily
        # inside __aenter__ to avoid importing the heavy playwright package at
        # module load time.
        self._playwright: Any = None
        self._browser: Any = None

    async def __aenter__(self) -> BrowserManager:
        from playwright.async_api import async_playwright

        self._playwright = await async_playwright().start()
        launch_kwargs: dict[str, Any] = {"headless": self._headless}
        if self._proxy:
            launch_kwargs["proxy"] = {"server": self._proxy}
        self._browser = await self._playwright.chromium.launch(**launch_kwargs)
        logger.debug("browser_started", headless=self._headless, proxy=bool(self._proxy))
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        logger.debug("browser_stopped")

    async def get_page_content(
        self,
        url: str,
        wait_for_selector: str | None = None,
        extra_timeout_ms: int = 0,
    ) -> str:
        """
        Navigate to URL, optionally wait for a CSS selector, return full HTML.

        Args:
            url: Target URL.
            wait_for_selector: CSS selector to wait for after navigation (optional).
            extra_timeout_ms: Additional ms to wait on top of the default timeout.
        """
        assert self._browser is not None, "BrowserManager used outside async context"

        timeout = self._timeout_ms + extra_timeout_ms
        page = await self._browser.new_page()
        try:
            await page.goto(url, wait_until=_WAIT_UNTIL, timeout=timeout)
            if wait_for_selector:
                await page.wait_for_selector(wait_for_selector, timeout=timeout)
            html: str = await page.content()
            logger.debug("browser_page_fetched", url=url, html_len=len(html))
            return html
        finally:
            await page.close()

    async def get_page_text(self, url: str, selector: str) -> str:
        """Extract inner text of a CSS selector from a page."""
        assert self._browser is not None
        page = await self._browser.new_page()
        try:
            await page.goto(url, wait_until=_WAIT_UNTIL, timeout=self._timeout_ms)
            element = await page.query_selector(selector)
            return await element.inner_text() if element else ""
        finally:
            await page.close()
