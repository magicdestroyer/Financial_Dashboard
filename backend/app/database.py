"""
Async SQLAlchemy engine + session factory.

Key concept: FastAPI route handlers receive a *session* through
dependency injection (get_db).  Each request gets its own session
that's committed or rolled back automatically.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# The async engine manages a pool of database connections.
# echo=False in production; set True for SQL debugging.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
)

# Session factory — each call produces a fresh AsyncSession
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # prevents lazy-load errors after commit
)


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


async def get_db():
    """
    FastAPI dependency that yields a database session.

    Usage in a route:
        async def my_route(db: AsyncSession = Depends(get_db)):
            ...

    The session auto-closes when the request finishes.
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()