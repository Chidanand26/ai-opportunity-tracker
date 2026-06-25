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
        # structlog.stdlib.add_logger_name is intentionally absent:
        # it reads logger.name, which exists on stdlib logging.Logger but not
        # on PrintLogger (which only has _file/_write/_flush). The module name
        # is injected via get_logger().bind(logger=name) instead.
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
    """
    Return a structlog logger with the module name pre-bound.

    Usage: logger = get_logger(__name__)

    The name is injected as logger=<name> in the event dict so it appears in
    every log line. We bind it explicitly because PrintLoggerFactory ignores
    positional arguments passed to structlog.get_logger(), so passing the name
    there has no effect.
    """
    return structlog.get_logger().bind(logger=name)
