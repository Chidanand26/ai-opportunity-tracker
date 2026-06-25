from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    All configuration is read from environment variables (or a .env file).
    No secrets ever live in source code — see .env.example for the full list.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        # Extra fields in .env are silently ignored — safe for partial configs
        extra="ignore",
    )

    # ── Application ───────────────────────────────────────────────────────────
    app_name: str = "AI Opportunity Tracker"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"

    # Required — no default so a missing value fails loudly at startup
    secret_key: str

    # ── CORS ──────────────────────────────────────────────────────────────────
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # ── Database ──────────────────────────────────────────────────────────────
    database_url: str  # e.g. postgresql+asyncpg://user:pass@host:5432/db

    # ── Redis ─────────────────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── Celery (inherit from Redis if not explicitly set) ─────────────────────
    celery_broker_url: str = ""
    celery_result_backend: str = ""

    # ── LLM ───────────────────────────────────────────────────────────────────
    llm_provider: Literal["anthropic", "openai"] = "anthropic"
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    llm_model: str = "claude-sonnet-4-6"

    # ── Email ─────────────────────────────────────────────────────────────────
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    notification_from_email: str = ""

    # ── Single-user MVP ───────────────────────────────────────────────────────
    # Every user-scoped service takes a user_id parameter; this is the default.
    # Multi-user migration: add auth provider settings here, remove this default.
    default_user_id: int = 1

    @model_validator(mode="after")
    def _fill_celery_defaults(self) -> "Settings":
        """Celery broker/backend default to the Redis URL when not explicitly set."""
        if not self.celery_broker_url:
            self.celery_broker_url = self.redis_url
        if not self.celery_result_backend:
            self.celery_result_backend = self.redis_url
        return self

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


# Module-level singleton — import this everywhere instead of re-instantiating.
# Required fields are supplied from the environment; the pydantic mypy plugin
# understands this, so no call-arg ignore is needed.
settings = Settings()
