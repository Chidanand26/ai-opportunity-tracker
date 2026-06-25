"""
Integration test fixtures shared across all repository tests.

Requires:
  - PostgreSQL running (docker compose up -d db)
  - DATABASE_URL set in the environment (via .env)

Event-loop correctness (the critical part):
  asyncpg connections are bound to the event loop that created them. If the
  engine lives on one loop (session scope) and a test runs on another (function
  scope), the first query raises "Task got Future attached to a different loop",
  surfaced by SQLAlchemy as InterfaceError.

  To avoid that, every async fixture AND every async test in this package runs
  on a single session-scoped event loop:
    - asyncio_default_fixture_loop_scope = "session"  (pyproject.toml)
    - pytestmark = pytest.mark.asyncio(loop_scope="session")  (in test modules)
    - loop_scope="session" on the fixtures below
  We do NOT override the `event_loop` fixture — that approach is deprecated in
  pytest-asyncio 0.23+ and is itself a cause of the RuntimeError seen here.

Isolation strategy:
  The schema is created once per session. Each test runs against a session bound
  to a single connection wrapped in an outer transaction that is rolled back at
  the end of the test, so no data leaks between tests. `join_transaction_mode=
  "create_savepoint"` means even an inner commit only commits a SAVEPOINT, never
  the outer transaction — isolation holds regardless of what the code under test
  does.
"""

from collections.abc import AsyncGenerator

import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.infrastructure.db.models import Base


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    One engine + schema for the whole session, pinned to the session loop.

    NullPool ensures no connection is cached and later reused on a stale loop —
    a second layer of defence against cross-loop asyncpg errors.
    """
    eng = create_async_engine(settings.database_url, echo=False, poolclass=NullPool)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture(loop_scope="session")
async def session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """
    Per-test session bound to a single connection inside an outer transaction
    that is always rolled back — fast, fully isolated, no schema rebuild per test.
    """
    conn: AsyncConnection = await engine.connect()
    trans = await conn.begin()
    factory = async_sessionmaker(
        bind=conn,
        class_=AsyncSession,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )
    sess = factory()
    try:
        yield sess
    finally:
        await sess.close()
        await trans.rollback()
        await conn.close()
