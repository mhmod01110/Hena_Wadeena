"""Guide service database setup."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import Column, inspect, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateColumn

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
        await conn.run_sync(_reconcile_profiles_schema)
        await conn.run_sync(_seed_data)


def _reconcile_profiles_schema(sync_conn) -> None:
    from models import GuideProfile

    inspector = inspect(sync_conn)
    if "profiles" not in inspector.get_table_names():
        return

    table = GuideProfile.__table__
    existing_columns = {col["name"] for col in inspector.get_columns(table.name)}

    for model_col in table.columns:
        if model_col.name in existing_columns:
            continue
        # Keep migration additive and permissive for existing rows.
        migration_col = Column(model_col.name, model_col.type, nullable=True)
        ddl = str(CreateColumn(migration_col).compile(dialect=sync_conn.dialect))
        sync_conn.execute(text(f"ALTER TABLE {table.name} ADD COLUMN {ddl}"))

    # Backfill nullable legacy rows so service logic sees consistent defaults.
    defaults = {
        "entity_kind": "guide_profile",
        "rating_avg": 0,
        "rating_count": 0,
        "total_bookings": 0,
        "total_earnings": 0,
        "package_active": True,
        "duration_hrs": 8,
        "payment_status": "unpaid",
        "guide_penalty": False,
        "review_submitted": False,
        "review_active": True,
    }
    refreshed_columns = {col["name"] for col in inspect(sync_conn).get_columns(table.name)}
    for col_name, default_value in defaults.items():
        if col_name not in refreshed_columns:
            continue
        sync_conn.execute(
            text(f"UPDATE {table.name} SET {col_name} = :default_value WHERE {col_name} IS NULL"),
            {"default_value": default_value},
        )

    for idx in table.indexes:
        idx.create(bind=sync_conn, checkfirst=True)


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

        seed_package = GuideProfile(
            title=f"package:{rows[0].id}:desert-day",
            description="Day package in Western Desert",
            status="active",
            entity_kind="package",
            package_guide_profile_id=rows[0].id,
            package_title="Western Desert Explorer",
            package_description="Full-day route with heritage stops and desert picnic.",
            package_duration_hrs=8,
            package_max_people=6,
            package_price=950,
            package_category="desert",
            package_includes_csv="Guide,4x4 transport,Water",
            package_images_csv="https://source.unsplash.com/1200x800/?desert-tour",
            package_active=True,
        )
        session.add(seed_package)
        session.flush()

        seed_pending_booking = GuideProfile(
            title="booking:demo-booking-pending",
            description="Seed pending booking",
            status="pending",
            entity_kind="booking",
            guide_profile_id=rows[0].id,
            guide_user_id=rows[0].user_id,
            guide_display_name=rows[0].display_name,
            tourist_id="00000000-0000-0000-0000-000000000004",
            package_id=seed_package.id,
            booking_package_title=seed_package.package_title,
            booking_date="2026-03-22",
            start_time="08:00",
            duration_hrs=8,
            people_count=2,
            total_price=1900,
            payment_status="unpaid",
            notes="Desert tour package",
            review_submitted=False,
        )
        session.add(seed_pending_booking)

        seed_completed_booking = GuideProfile(
            title="booking:demo-booking-completed",
            description="Seed completed booking",
            status="completed",
            entity_kind="booking",
            guide_profile_id=rows[0].id,
            guide_user_id=rows[0].user_id,
            guide_display_name=rows[0].display_name,
            tourist_id="00000000-0000-0000-0000-000000000011",
            package_id=seed_package.id,
            booking_package_title=seed_package.package_title,
            booking_date="2026-03-10",
            start_time="09:00",
            duration_hrs=8,
            people_count=3,
            total_price=2850,
            payment_status="paid",
            notes="Completed seed trip",
            review_submitted=True,
        )
        session.add(seed_completed_booking)
        session.flush()

        session.add(
            GuideProfile(
                title=f"review:{rows[0].id}:{seed_completed_booking.id}",
                description="Amazing tour and storytelling",
                status="active",
                entity_kind="review",
                review_guide_profile_id=rows[0].id,
                review_booking_id=seed_completed_booking.id,
                review_tourist_id=seed_completed_booking.tourist_id,
                review_tourist_name="Seed Tourist",
                review_rating=5,
                review_comment="Amazing tour and storytelling",
                review_guide_reply="Thank you for your visit.",
                review_active=True,
            )
        )
        rows[0].rating_avg = 5
        rows[0].rating_count = 1
        rows[0].total_bookings = 1
        rows[0].total_earnings = 2850

        session.commit()
    finally:
        session.close()
