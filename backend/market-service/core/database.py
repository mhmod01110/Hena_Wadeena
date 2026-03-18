"""Market service database setup."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from shared.core.database import create_db_engine, create_session_factory, Base, ensure_database_exists
from core.config import settings

engine = create_db_engine(settings.MARKET_DATABASE_URL, echo=settings.DEBUG)
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
    await ensure_database_exists(settings.MARKET_DATABASE_URL, echo=settings.DEBUG)
    import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_seed_data)


def _seed_data(sync_conn) -> None:
    from models import Listing

    session = Session(bind=sync_conn)
    try:
        if session.query(Listing).count() > 0:
            return

        listings = [
            Listing(
                title="Green Valley Farms",
                description="Premium dates and olives supplier",
                status="active",
                owner_id="00000000-0000-0000-0000-000000000006",
                listing_type="sell",
                category="supplier",
                location="Kharga",
                price=55,
                currency="EGP",
                is_verified=True,
            ),
            Listing(
                title="Golden Palm Co",
                description="Date producer for local and export channels",
                status="active",
                owner_id="00000000-0000-0000-0000-000000000006",
                listing_type="sell",
                category="supplier",
                location="Dakhla",
                price=48,
                currency="EGP",
                is_verified=True,
            ),
            Listing(
                title="Kharga Furnished Apartment",
                description="Furnished apartment suitable for students",
                status="active",
                owner_id="00000000-0000-0000-0000-000000000007",
                listing_type="rent",
                category="accommodation",
                location="Kharga",
                price=1800,
                currency="EGP",
                is_verified=False,
            ),
            Listing(
                title="Oasis Hotel",
                description="Hotel room close to city center",
                status="active",
                owner_id="00000000-0000-0000-0000-000000000006",
                listing_type="rent",
                category="accommodation",
                location="Kharga",
                price=450,
                currency="EGP",
                is_verified=True,
            ),
            Listing(
                title="Farafra Dates Cooperative",
                description="Bulk date supplier for wholesale buyers",
                status="active",
                owner_id="00000000-0000-0000-0000-000000000008",
                listing_type="sell",
                category="supplier",
                location="Farafra",
                price=52,
                currency="EGP",
                is_verified=False,
            ),
        ]

        session.add_all(listings)
        session.commit()
    finally:
        session.close()