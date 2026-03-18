"""Analytics service database setup."""

import os
import sys

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from core.config import settings
from shared.core.database import Base, create_db_engine, create_session_factory, ensure_database_exists

engine = create_db_engine(settings.ANALYTICS_DATABASE_URL, echo=settings.DEBUG)
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
    await ensure_database_exists(settings.ANALYTICS_DATABASE_URL, echo=settings.DEBUG)
    import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_seed_data)


def _seed_data(sync_conn) -> None:
    from models import MetricEvent

    session = Session(bind=sync_conn)
    try:
        if session.query(MetricEvent).count() > 0:
            return

        rows = [
            MetricEvent(
                title="seed:event:user-created-tourist",
                status="recorded",
                event_type="auth.user.created",
                actor_id="00000000-0000-0000-0000-000000000004",
                actor_role="tourist",
                entity_type="user",
                entity_id="00000000-0000-0000-0000-000000000004",
                city="Kharga",
            ),
            MetricEvent(
                title="seed:event:user-created-investor",
                status="recorded",
                event_type="auth.user.created",
                actor_id="00000000-0000-0000-0000-000000000005",
                actor_role="investor",
                entity_type="user",
                entity_id="00000000-0000-0000-0000-000000000005",
                city="Kharga",
            ),
            MetricEvent(
                title="seed:event:listing-created",
                status="recorded",
                event_type="market.listing.created",
                actor_id="00000000-0000-0000-0000-000000000006",
                actor_role="merchant",
                entity_type="listing",
                entity_id="seed-listing-1",
                city="Kharga",
                list_price=1800,
            ),
            MetricEvent(
                title="seed:event:listing-verified",
                status="recorded",
                event_type="market.listing.verified",
                actor_id="00000000-0000-0000-0000-000000000001",
                actor_role="admin",
                entity_type="listing",
                entity_id="seed-listing-1",
                city="Kharga",
            ),
            MetricEvent(
                title="seed:event:booking-requested",
                status="recorded",
                event_type="guide.booking.requested",
                actor_id="00000000-0000-0000-0000-000000000004",
                actor_role="tourist",
                entity_type="booking",
                entity_id="seed-booking-1",
            ),
            MetricEvent(
                title="seed:event:booking-confirmed",
                status="recorded",
                event_type="guide.booking.confirmed",
                actor_id="00000000-0000-0000-0000-000000000003",
                actor_role="guide",
                entity_type="booking",
                entity_id="seed-booking-1",
            ),
            MetricEvent(
                title="seed:event:booking-completed",
                status="recorded",
                event_type="guide.booking.completed",
                actor_id="00000000-0000-0000-0000-000000000003",
                actor_role="guide",
                entity_type="booking",
                entity_id="seed-booking-1",
            ),
            MetricEvent(
                title="seed:event:payment-checkout",
                status="recorded",
                event_type="payment.checkout",
                actor_id="00000000-0000-0000-0000-000000000004",
                actor_role="tourist",
                entity_type="transaction",
                entity_id="seed-tx-1",
                amount=1200,
                payment_method="wallet",
            ),
            MetricEvent(
                title="seed:event:search-query-hotel",
                status="recorded",
                event_type="search.query",
                actor_id="00000000-0000-0000-0000-000000000004",
                actor_role="tourist",
                search_query="kharga hotel",
                results_count=3,
            ),
            MetricEvent(
                title="seed:event:search-query-investment",
                status="recorded",
                event_type="search.query",
                actor_id="00000000-0000-0000-0000-000000000005",
                actor_role="investor",
                search_query="farm project",
                results_count=2,
            ),
        ]

        session.add_all(rows)
        session.commit()
    finally:
        session.close()
