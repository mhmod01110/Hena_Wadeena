"""Payment service database setup."""

import os
import sys

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from core.config import settings
from shared.core.database import Base, create_db_engine, create_session_factory, ensure_database_exists

engine = create_db_engine(settings.PAYMENT_DATABASE_URL, echo=settings.DEBUG)
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
    await ensure_database_exists(settings.PAYMENT_DATABASE_URL, echo=settings.DEBUG)
    import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_seed_data)


def _seed_data(sync_conn) -> None:
    from models import WalletTransaction

    session = Session(bind=sync_conn)
    try:
        if session.query(WalletTransaction).count() > 0:
            return

        rows = [
            WalletTransaction(
                title="seed:tx:tourist:topup",
                status="completed",
                user_id="00000000-0000-0000-0000-000000000004",
                tx_type="topup",
                direction="credit",
                amount=3000,
                balance_after=3000,
                payment_method="visa",
                description="Initial wallet topup",
            ),
            WalletTransaction(
                title="seed:tx:tourist:booking-checkout",
                status="completed",
                user_id="00000000-0000-0000-0000-000000000004",
                tx_type="checkout",
                direction="debit",
                amount=1200,
                balance_after=1800,
                payment_method="wallet",
                reference_type="booking",
                reference_id="seed-booking-1",
                description="Guide booking payment",
            ),
            WalletTransaction(
                title="seed:tx:guide:earning",
                status="completed",
                user_id="00000000-0000-0000-0000-000000000003",
                tx_type="topup",
                direction="credit",
                amount=2200,
                balance_after=2200,
                payment_method="platform_transfer",
                description="Platform payout received",
            ),
            WalletTransaction(
                title="seed:tx:merchant:topup",
                status="completed",
                user_id="00000000-0000-0000-0000-000000000006",
                tx_type="topup",
                direction="credit",
                amount=5000,
                balance_after=5000,
                payment_method="bank",
                description="Merchant wallet topup",
            ),
        ]

        session.add_all(rows)
        session.commit()
    finally:
        session.close()
