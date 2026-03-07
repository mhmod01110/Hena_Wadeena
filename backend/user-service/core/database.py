"""User service database setup."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy.ext.asyncio import AsyncSession
from shared.core.database import create_db_engine, create_session_factory, Base
from core.config import settings

engine = create_db_engine(settings.USER_DATABASE_URL, echo=settings.DEBUG)
SessionFactory = create_session_factory(engine)


async def get_session() -> AsyncSession:
    async with SessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db():
    import models  # noqa
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
