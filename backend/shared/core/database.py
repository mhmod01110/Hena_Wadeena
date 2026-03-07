"""Database engine and session factory — Factory Pattern."""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def create_db_engine(database_url: str, echo: bool = False) -> AsyncEngine:
    """Factory: create an async SQLAlchemy engine."""
    return create_async_engine(
        database_url,
        echo=echo,
        pool_size=5,
        max_overflow=10,
    )


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Factory: create a session maker bound to an engine."""
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def init_models(engine: AsyncEngine):
    """Create all tables from Base metadata."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
