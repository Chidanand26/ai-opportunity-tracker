"""
Integration test fixtures shared across all repository tests.

Requires:
  - PostgreSQL running (docker compose up -d db)
  - DATABASE_URL set in the environment (via .env)

Isolation strategy:
  - Tables are created once per session and dropped after.
  - Each test wraps its work in a SAVEPOINT, then rolls back to it.
    This gives per-test isolation without recreating the schema on every test.
"""

import asyncio
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.infrastructure.db.models import Base


@pytest.fixture(scope="session")
def event_loop():
    """Single event loop shared by all tests in the integration session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def engine():
    """One engine + schema for the whole session."""
    _engine = create_async_engine(settings.database_url, echo=False)
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield _engine
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await _engine.dispose()


@pytest_asyncio.fixture
async def session(engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Per-test session using a nested transaction (SAVEPOINT).

    The outer transaction is never committed; the inner SAVEPOINT is rolled
    back after each test so no data leaks between tests.
    """
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as sess:
        # Begin an outer transaction — never committed
        await sess.begin()
        # Create a SAVEPOINT so individual tests can flush without committing
        await sess.begin_nested()
        try:
            yield sess
        finally:
            # Roll back to the SAVEPOINT, then close the outer transaction
            await sess.rollback()
