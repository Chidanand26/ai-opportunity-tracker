"""
Scraper exception hierarchy.

All exceptions are catchable at different granularities:
  - Catch ScraperError for any scraping failure.
  - Catch FetchError for network/HTTP problems.
  - Catch ParseError for malformed content.
"""


class ScraperError(Exception):
    """Root of the scraper exception tree."""


# ── Fetch-layer exceptions ────────────────────────────────────────────────────

class FetchError(ScraperError):
    """Failed to retrieve a URL."""

    def __init__(self, url: str, reason: str) -> None:
        self.url = url
        self.reason = reason
        super().__init__(f"Failed to fetch {url!r}: {reason}")


class RobotsBlockedError(FetchError):
    """robots.txt disallows fetching this URL for our user-agent."""

    def __init__(self, url: str, user_agent: str) -> None:
        self.user_agent = user_agent
        super().__init__(url, f"disallowed for user-agent {user_agent!r}")


class RateLimitedError(FetchError):
    """Domain rate limit exhausted; caller should back off."""


class HttpError(FetchError):
    """Non-retryable HTTP error (e.g. 403, 404, 410)."""

    def __init__(self, url: str, status_code: int) -> None:
        self.status_code = status_code
        super().__init__(url, f"HTTP {status_code}")


# ── Content-layer exceptions ──────────────────────────────────────────────────

class ValidationError(ScraperError):
    """Fetched content failed validation checks (wrong type, too short, etc.)."""

    def __init__(self, url: str, reason: str) -> None:
        self.url = url
        self.reason = reason
        super().__init__(f"Validation failed for {url!r}: {reason}")


class ParseError(ScraperError):
    """Could not extract postings from valid content."""

    def __init__(self, url: str, reason: str) -> None:
        self.url = url
        self.reason = reason
        super().__init__(f"Parse failed for {url!r}: {reason}")


# ── Persist-layer exceptions ──────────────────────────────────────────────────

class PersistError(ScraperError):
    """Failed to save scraped data to the database."""
