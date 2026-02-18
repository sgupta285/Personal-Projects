"""
Database engine setup with connection pooling.
Supports both PostgreSQL (production) and SQLite (local development).
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


def _build_engine():
    url = settings.database_url
    is_sqlite = url.startswith("sqlite")

    kwargs = {}
    if not is_sqlite:
        # PostgreSQL connection pooling
        kwargs.update(
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            pool_timeout=settings.db_pool_timeout,
            pool_recycle=settings.db_pool_recycle,
            pool_pre_ping=True,
        )
    else:
        # Ensure data directory exists for SQLite
        db_path = url.replace("sqlite+aiosqlite:///", "")
        if db_path.startswith("./"):
            db_dir = os.path.dirname(db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)

    return create_async_engine(url, echo=settings.db_echo, **kwargs)


engine = _build_engine()
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    """Dependency that yields an async database session."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Create all tables."""
    async with engine.begin() as conn:
        from app.models import orm  # noqa: ensure models are registered
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    await engine.dispose()
