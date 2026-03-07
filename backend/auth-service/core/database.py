"""Auth service database setup + session dependency."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy.ext.asyncio import AsyncSession

from shared.core.database import create_db_engine, create_session_factory, Base
from core.config import settings

engine = create_db_engine(settings.AUTH_DATABASE_URL, echo=settings.DEBUG)
SessionFactory = create_session_factory(engine)


async def get_session() -> AsyncSession:
    """FastAPI dependency: yields a DB session with auto-commit/rollback."""
    async with SessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db():
    """Create all auth tables on startup."""
    # Import models so they register with Base.metadata
    import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
