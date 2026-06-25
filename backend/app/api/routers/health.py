from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str


class ReadinessResponse(HealthResponse):
    database: str
    redis: str


@router.get("/", response_model=HealthResponse, summary="Liveness check")
async def liveness() -> HealthResponse:
    """Returns 200 when the process is running. Used by load balancers."""
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        environment=settings.environment,
    )


@router.get("/ready", response_model=ReadinessResponse, summary="Readiness check")
async def readiness() -> ReadinessResponse:
    """
    Returns 200 only when DB and Redis are reachable.
    Orchestrators (k8s, ECS) use this to gate traffic.
    """
    from app.infrastructure.cache.redis_client import check_redis_connection
    from app.infrastructure.db.session import check_db_connection

    db_ok = await check_db_connection()
    redis_ok = await check_redis_connection()

    return ReadinessResponse(
        status="ok" if (db_ok and redis_ok) else "degraded",
        version=settings.app_version,
        environment=settings.environment,
        database="ok" if db_ok else "unreachable",
        redis="ok" if redis_ok else "unreachable",
    )
