from redis.asyncio import Redis, from_url

from app.core.config import settings

# Module-level client — shared across all async tasks in the same process.
# Call close() on shutdown (handled in main.py lifespan).
_redis: Redis | None = None


def get_redis() -> Redis:
    """Return the shared Redis client, initialising it on first call."""
    global _redis
    if _redis is None:
        _redis = from_url(settings.redis_url, decode_responses=True)
    return _redis


async def check_redis_connection() -> bool:
    """Ping Redis — used by the readiness health check."""
    try:
        r = get_redis()
        return await r.ping()
    except Exception:
        return False


async def close_redis() -> None:
    """Gracefully close the Redis connection pool."""
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None
