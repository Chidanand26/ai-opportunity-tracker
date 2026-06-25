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

    Startup:  initialise connections, warm caches, log readiness.
    Shutdown: close connections cleanly (avoids connection pool warnings).

    Future additions: db engine, redis pool, celery inspect.
    """
    setup_logging()
    logger.info("starting", app=settings.app_name, env=settings.environment)
    yield
    logger.info("shutting down", app=settings.app_name)


def create_app() -> FastAPI:
    """
    Application factory — returns a fully configured FastAPI instance.

    Using a factory (rather than a module-level app) makes the app easy to
    test in isolation: each test can call create_app() with a fresh state.
    """
    from app.api.routers import health  # local import avoids circular deps at init

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "AI-powered tracker for internships, research positions, "
            "fellowships, scholarships, and more."
        ),
        # Disable interactive docs in production (security best practice)
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

    # Routers — each feature adds its own router here as we build it out
    app.include_router(health.router, prefix="/health", tags=["health"])

    return app


# Module-level instance used by uvicorn and docker-compose
app = create_app()
