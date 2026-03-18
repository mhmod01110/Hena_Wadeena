"""Map service database setup."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from shared.core.database import create_db_engine, create_session_factory, Base, ensure_database_exists
from core.config import settings

engine = create_db_engine(settings.MAP_DATABASE_URL, echo=settings.DEBUG)
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
    await ensure_database_exists(settings.MAP_DATABASE_URL, echo=settings.DEBUG)
    import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_seed_data)


def _seed_data(sync_conn) -> None:
    from models import PointOfInterest

    session = Session(bind=sync_conn)
    try:
        if session.query(PointOfInterest).count() > 0:
            return

        pois = [
            PointOfInterest(
                title="poi:kharga-temple",
                description="Historic temple in Kharga oasis",
                status="approved",
                entity_kind="poi",
                created_by="00000000-0000-0000-0000-000000000001",
                name_ar="معبد هيبس",
                name_en="Hibis Temple",
                category="landmark",
                address="Kharga, New Valley",
                lat=25.451,
                lng=30.5434,
                phone="0927921111",
            ),
            PointOfInterest(
                title="poi:white-desert",
                description="White Desert camp area",
                status="approved",
                entity_kind="poi",
                created_by="00000000-0000-0000-0000-000000000001",
                name_ar="الصحراء البيضاء",
                name_en="White Desert",
                category="nature",
                address="Farafra, New Valley",
                lat=27.2956,
                lng=28.0567,
            ),
            PointOfInterest(
                title="poi:kharga-station",
                description="Central transport station",
                status="approved",
                entity_kind="poi",
                created_by="00000000-0000-0000-0000-000000000001",
                name_ar="محطة الخارجة الرئيسية",
                name_en="Kharga Central Station",
                category="station",
                address="Kharga Center",
                lat=25.44,
                lng=30.55,
                phone="0927923333",
            ),
            PointOfInterest(
                title="carpool:kharga-assiut",
                description="Morning ride",
                status="open",
                entity_kind="carpool_ride",
                driver_id="00000000-0000-0000-0000-000000000007",
                origin_name="Kharga",
                destination_name="Assiut",
                departure_time="2026-03-20T07:00:00",
                seats_total=4,
                seats_taken=1,
                price_per_seat=120,
                notes="Toyota sedan",
            ),
            PointOfInterest(
                title="carpool:dakhla-kharga",
                description="Evening ride",
                status="open",
                entity_kind="carpool_ride",
                driver_id="00000000-0000-0000-0000-000000000003",
                origin_name="Dakhla",
                destination_name="Kharga",
                departure_time="2026-03-21T17:30:00",
                seats_total=3,
                seats_taken=0,
                price_per_seat=95,
                notes="SUV",
            ),
        ]

        session.add_all(pois)
        session.commit()
    finally:
        session.close()