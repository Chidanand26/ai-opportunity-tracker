"""
Per-domain rate limiter — prevents hammering a single host.

Current implementation: in-memory leaky bucket per domain.
Works correctly for a single Celery worker process.

Upgrade path to multi-worker: replace the in-memory dict with a Redis
sorted-set sliding window. Key: "rate_limit:{domain}", members are
timestamps, window is 60 seconds. Use a Lua script for atomic check+insert.
The interface (acquire/release) stays the same.
"""

import asyncio
import time
from collections import defaultdict
from urllib.parse import urlparse

from app.core.logging import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """
    Async per-domain leaky bucket.

    Ensures no more than `requests_per_minute` requests are sent to any
    single domain within a 60-second sliding window.

    Thread-safety: safe within a single asyncio event loop (one lock per domain).
    Not safe across processes — use the Redis upgrade for multi-worker setups.
    """

    def __init__(self, requests_per_minute: int = 10) -> None:
        self._rpm = requests_per_minute
        self._interval = 60.0 / requests_per_minute   # min seconds between requests
        self._last_request: dict[str, float] = defaultdict(float)
        self._locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

    @staticmethod
    def _domain(url: str) -> str:
        parsed = urlparse(url)
        return parsed.netloc or url

    async def acquire(self, url: str) -> None:
        """
        Block until a request slot is available for the URL's domain.
        Callers should call this before every HTTP request.
        """
        domain = self._domain(url)
        async with self._locks[domain]:
            now = time.monotonic()
            elapsed = now - self._last_request[domain]
            if elapsed < self._interval:
                wait = self._interval - elapsed
                logger.debug(
                    "rate_limit_wait",
                    domain=domain,
                    wait_ms=round(wait * 1000),
                )
                await asyncio.sleep(wait)
            self._last_request[domain] = time.monotonic()

    def set_rate(self, requests_per_minute: int) -> None:
        """Dynamically adjust the rate limit (e.g. after a 429 response)."""
        self._rpm = requests_per_minute
        self._interval = 60.0 / requests_per_minute
