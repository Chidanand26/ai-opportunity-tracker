"""
BaseRepository — thin wrapper that gives every concrete repo an AsyncSession.

Every repository receives its session from FastAPI's get_db() dependency,
which handles commit and rollback at the request boundary.
Repositories call flush() to materialise writes within the current
transaction without committing; the caller decides when to commit.
"""

from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
