"""Database engine and session factory — Factory Pattern."""

import asyncio

from sqlalchemy import text
from sqlalchemy.engine import make_url
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


def _quote_mysql_identifier(name: str) -> str:
    return "`" + name.replace("`", "``") + "`"


async def ensure_database_exists(database_url: str, echo: bool = False) -> None:
    """Create target MySQL database if it does not exist."""
    url = make_url(database_url)
    db_name = url.database
    if not db_name:
        return

    # Important: database=None keeps original DB in SQLAlchemy URL;
    # use empty string to connect to server without selecting a schema.
    admin_url = url.set(database="")

    last_error = None
    for attempt in range(1, 16):
        admin_engine = create_async_engine(admin_url, echo=echo, pool_pre_ping=True)
        try:
            async with admin_engine.begin() as conn:
                await conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {_quote_mysql_identifier(db_name)}"))
                return
        except Exception as exc:  # pragma: no cover
            last_error = exc
            await asyncio.sleep(min(0.5 * attempt, 3.0))
        finally:
            await admin_engine.dispose()

    raise last_error
