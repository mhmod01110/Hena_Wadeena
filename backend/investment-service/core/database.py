"""Investment service database setup."""

import os
import sys

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from core.config import settings
from shared.core.database import Base, create_db_engine, create_session_factory, ensure_database_exists

engine = create_db_engine(settings.INVESTMENT_DATABASE_URL, echo=settings.DEBUG)
SessionFactory = create_session_factory(engine)


async def get_session() -> AsyncSession:
    async with SessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    await ensure_database_exists(settings.INVESTMENT_DATABASE_URL, echo=settings.DEBUG)
    import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_seed_data)


def _seed_data(sync_conn) -> None:
    from models import Opportunity

    session = Session(bind=sync_conn)
    try:
        if session.query(Opportunity).count() > 0:
            return

        rows = [
            Opportunity(
                title="Integrated Farm Project",
                description="100-acre farm for dates and olives with modern irrigation.",
                status="open",
                entity_kind="opportunity",
                owner_id="00000000-0000-0000-0000-000000000005",
                category="agriculture",
                location="Kharga",
                min_investment=5000000,
                max_investment=10000000,
                expected_roi="18-22%",
                is_verified=True,
            ),
            Opportunity(
                title="Eco Tourism Compound",
                description="Eco-lodge and desert camp package near White Desert.",
                status="open",
                entity_kind="opportunity",
                owner_id="00000000-0000-0000-0000-000000000006",
                category="tourism",
                location="Farafra",
                min_investment=15000000,
                max_investment=25000000,
                expected_roi="20-25%",
                is_verified=False,
            ),
            Opportunity(
                title="Solar Irrigation Network",
                description="Deploy a shared solar-powered irrigation network for medium-size farms.",
                status="open",
                entity_kind="opportunity",
                owner_id="00000000-0000-0000-0000-000000000008",
                category="infrastructure",
                location="Dakhla",
                min_investment=3000000,
                max_investment=7000000,
                expected_roi="15-19%",
                is_verified=True,
            ),
        ]

        session.add_all(rows)
        session.flush()

        interests = [
            Opportunity(
                title=f"Interest {rows[1].id} by investor-005",
                description="Interested in co-investing with operational partner.",
                status="submitted",
                entity_kind="interest",
                opportunity_id=rows[1].id,
                investor_id="00000000-0000-0000-0000-000000000005",
                message="Interested in co-investing with operational partner.",
            ),
            Opportunity(
                title=f"Interest {rows[0].id} by investor-009",
                description="Requesting technical due diligence details.",
                status="reviewed",
                entity_kind="interest",
                opportunity_id=rows[0].id,
                investor_id="00000000-0000-0000-0000-000000000009",
                message="Requesting technical due diligence details.",
            ),
        ]

        session.add_all(interests)
        session.commit()
    finally:
        session.close()