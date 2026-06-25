import logging
import sys

import structlog

from app.core.config import settings


def setup_logging() -> None:
    """
    Configure structured logging using structlog.

    Dev mode:  human-readable colored console output.
    Prod mode: machine-readable JSON — compatible with log aggregators
               (Datadog, CloudWatch, GCP Logging, etc.)
    """
    log_level = logging.DEBUG if settings.debug else logging.INFO

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
    ]

    if settings.debug:
        # Pretty output with colors for local development
        renderer: structlog.types.Processor = structlog.dev.ConsoleRenderer()
    else:
        # JSON lines — each log entry is one parseable JSON object
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
    )

    # Route stdlib logging (e.g. uvicorn, sqlalchemy) through structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )
    # Silence noisy libraries in production
    if not settings.debug:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.BoundLogger:
    """Return a named structlog logger. Use in every module that needs logging."""
    return structlog.get_logger(name)
