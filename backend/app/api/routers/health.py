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
    Returns 200 only when all dependencies (DB, Redis) are reachable.
    Used by orchestrators (k8s, ECS) to gate traffic.

    Future: add actual db ping and redis ping here.
    """
    return ReadinessResponse(
        status="ok",
        version=settings.app_version,
        environment=settings.environment,
        database="not_checked",  # TODO: implement in Step 4 (database layer)
        redis="not_checked",     # TODO: implement in Step 4
    )
