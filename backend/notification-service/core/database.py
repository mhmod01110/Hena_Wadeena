"""Notification service database setup."""

import os
import sys

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from core.config import settings
from shared.core.database import Base, create_db_engine, create_session_factory, ensure_database_exists

engine = create_db_engine(settings.NOTIFICATION_DATABASE_URL, echo=settings.DEBUG)
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
    await ensure_database_exists(settings.NOTIFICATION_DATABASE_URL, echo=settings.DEBUG)
    import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_seed_data)


def _seed_data(sync_conn) -> None:
    from models import NotificationMessage

    session = Session(bind=sync_conn)
    try:
        if session.query(NotificationMessage).count() > 0:
            return

        rows = [
            NotificationMessage(
                title="pref-tourist-004",
                description="Notification preferences",
                status="active",
                entity_kind="preference",
                user_id="00000000-0000-0000-0000-000000000004",
                notify_push=True,
                notify_email=True,
                notify_sms=False,
            ),
            NotificationMessage(
                title="pref-guide-003",
                description="Notification preferences",
                status="active",
                entity_kind="preference",
                user_id="00000000-0000-0000-0000-000000000003",
                notify_push=True,
                notify_email=True,
                notify_sms=True,
            ),
            NotificationMessage(
                title="notif-booking-confirmed-001",
                description="Your guide booking is confirmed.",
                status="sent",
                entity_kind="notification",
                user_id="00000000-0000-0000-0000-000000000004",
                notif_type="booking_confirmed",
                notif_title="Booking confirmed",
                notif_body="Your guide booking has been confirmed.",
                channel_csv="push,in_app",
                read_at=None,
            ),
            NotificationMessage(
                title="notif-payment-completed-002",
                description="Wallet payment completed.",
                status="sent",
                entity_kind="notification",
                user_id="00000000-0000-0000-0000-000000000004",
                notif_type="payment_completed",
                notif_title="Payment completed",
                notif_body="Payment was deducted from your wallet successfully.",
                channel_csv="in_app,email",
                read_at=None,
            ),
            NotificationMessage(
                title="notif-booking-requested-003",
                description="New booking request assigned.",
                status="sent",
                entity_kind="notification",
                user_id="00000000-0000-0000-0000-000000000003",
                notif_type="booking_requested",
                notif_title="New booking request",
                notif_body="You have a new booking request to review.",
                channel_csv="push,in_app",
                read_at=None,
            ),
        ]

        session.add_all(rows)
        session.commit()
    finally:
        session.close()