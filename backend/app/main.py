from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import get_logger, setup_logging

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Startup:  logging → DB engine ready → Redis client ready.
    Shutdown: close Redis connection pool cleanly.
    """
    setup_logging()
    logger.info("starting", app=settings.app_name, env=settings.environment)

    # Redis client is initialised lazily on first call — just import to wire it
    from app.infrastructure.cache.redis_client import get_redis
    get_redis()  # initialise the shared pool

    yield

    from app.infrastructure.cache.redis_client import close_redis
    await close_redis()
    logger.info("shutting down", app=settings.app_name)


def create_app() -> FastAPI:
    """
    Application factory — returns a fully configured FastAPI instance.

    Using a factory (rather than module-level construction) lets tests call
    create_app() in isolation without shared global state between test cases.
    """
    from app.api.routers import health

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "AI-powered tracker for internships, research positions, "
            "fellowships, scholarships, and more."
        ),
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix="/health", tags=["health"])

    return app


app = create_app()
