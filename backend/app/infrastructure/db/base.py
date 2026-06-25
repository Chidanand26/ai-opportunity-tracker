from sqlalchemy.orm import DeclarativeBase, MappedColumn, mapped_column
from sqlalchemy import DateTime, func
from datetime import datetime


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.

    Alembic's env.py imports this Base so autogenerate can detect
    schema changes across all models that inherit from it.

    To register a model for migrations: import it in
    app/infrastructure/db/models.py (which is imported by alembic/env.py).
    """

    # Common audit columns — every table inherits these
    created_at: MappedColumn[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: MappedColumn[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
