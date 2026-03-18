"""Guide service database setup."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from shared.core.database import create_db_engine, create_session_factory, Base, ensure_database_exists
from core.config import settings

engine = create_db_engine(settings.GUIDE_DATABASE_URL, echo=settings.DEBUG)
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
    await ensure_database_exists(settings.GUIDE_DATABASE_URL, echo=settings.DEBUG)
    import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_seed_data)


def _seed_data(sync_conn) -> None:
    from models import GuideProfile

    session = Session(bind=sync_conn)
    try:
        if session.query(GuideProfile).count() > 0:
            return

        rows = [
            GuideProfile(
                title="guide-profile:valley-guide",
                description="Licensed desert and heritage guide",
                status="active",
                entity_kind="guide_profile",
                user_id="00000000-0000-0000-0000-000000000003",
                display_name="Ahmed El Sayed",
                bio="Licensed desert and heritage guide",
                languages_csv="Arabic,English",
                specialties_csv="Desert safari,Heritage tours",
                base_price=900,
                active=True,
                verified=True,
            ),
            GuideProfile(
                title="guide-profile:oasis-explorer",
                description="Oasis and cultural tour specialist",
                status="active",
                entity_kind="guide_profile",
                user_id="00000000-0000-0000-0000-000000000007",
                display_name="Fatma Hassan",
                bio="Oasis and cultural tour specialist",
                languages_csv="Arabic,English,French",
                specialties_csv="Culture,Oasis tours",
                base_price=750,
                active=True,
                verified=False,
            ),
            GuideProfile(
                title="guide-profile:desert-navigator",
                description="Long-range safari and astronomy guide",
                status="active",
                entity_kind="guide_profile",
                user_id="00000000-0000-0000-0000-000000000010",
                display_name="Mina Saber",
                bio="Long-range safari and astronomy guide",
                languages_csv="Arabic,English",
                specialties_csv="Astronomy,Desert camping",
                base_price=1050,
                active=True,
                verified=True,
            ),
        ]

        session.add_all(rows)
        session.flush()

        session.add(
            GuideProfile(
                title="booking:demo-booking-1",
                description="Seed booking",
                status="confirmed",
                entity_kind="booking",
                guide_profile_id=rows[0].id,
                guide_user_id=rows[0].user_id,
                tourist_id="00000000-0000-0000-0000-000000000004",
                booking_date="2026-03-22",
                start_time="08:00",
                people_count=2,
                total_price=1800,
                notes="Desert tour package",
            )
        )

        session.commit()
    finally:
        session.close()