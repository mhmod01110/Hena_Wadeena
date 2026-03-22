"""Investment service database setup."""

import os
import sys

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from core.config import settings
from shared.core.database import Base, create_db_engine, create_session_factory, ensure_database_exists

engine = None
SessionFactory = None


def get_engine():
    global engine
    if engine is None:
        engine = create_db_engine(settings.INVESTMENT_DATABASE_URL, echo=settings.DEBUG)
    return engine


def get_session_factory():
    global SessionFactory
    if SessionFactory is None:
        SessionFactory = create_session_factory(get_engine())
    return SessionFactory


async def get_session() -> AsyncSession:
    async with get_session_factory()() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    await ensure_database_exists(settings.INVESTMENT_DATABASE_URL, echo=settings.DEBUG)
    import models  # noqa: F401

    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_seed_data)


def _seed_data(sync_conn) -> None:
    from models import InvestmentInterest, InvestmentOpportunity, InvestmentWatchlist

    session = Session(bind=sync_conn)
    try:
        if session.query(InvestmentOpportunity).count() > 0:
            return

        opportunities = [
            InvestmentOpportunity(
                owner_id="00000000-0000-0000-0000-000000000005",
                title="Integrated Farm Project",
                description="A 100-acre farm focused on dates and olives with modern irrigation and packing operations.",
                category="agriculture",
                opportunity_type="project",
                location="Kharga",
                min_investment=5000000,
                max_investment=10000000,
                expected_roi="18-22%",
                status="open",
                is_verified=True,
                interest_count=0,
            ),
            InvestmentOpportunity(
                owner_id="00000000-0000-0000-0000-000000000006",
                title="White Desert Eco Retreat",
                description="Eco-lodge and desert camp development near the White Desert for sustainable tourism.",
                category="tourism",
                opportunity_type="project",
                location="Farafra",
                min_investment=15000000,
                max_investment=25000000,
                expected_roi="20-25%",
                status="open",
                is_verified=True,
                interest_count=0,
            ),
            InvestmentOpportunity(
                owner_id="00000000-0000-0000-0000-000000000008",
                title="Solar Valley Startup",
                description="A startup building modular solar irrigation systems for medium-size farms in New Valley.",
                category="renewable_energy",
                opportunity_type="startup",
                location="Dakhla",
                min_investment=3000000,
                max_investment=7000000,
                expected_roi="15-19%",
                status="open",
                is_verified=True,
                interest_count=0,
            ),
            InvestmentOpportunity(
                owner_id="00000000-0000-0000-0000-000000000010",
                title="Industrial Packing Hub",
                description="Food processing and packing hub designed to serve local producers and export channels.",
                category="manufacturing",
                opportunity_type="partnership",
                location="Kharga",
                min_investment=7000000,
                max_investment=12000000,
                expected_roi="16-20%",
                status="pending_review",
                is_verified=False,
                interest_count=0,
            ),
        ]

        session.add_all(opportunities)
        session.flush()

        interests = [
            InvestmentInterest(
                opportunity_id=opportunities[0].id,
                investor_id="00000000-0000-0000-0000-000000000009",
                message="Interested in co-investing and reviewing the irrigation operations.",
                contact_name="Investor Nine",
                contact_email="investor9@example.com",
                contact_phone="+201000000009",
                company_name="Desert Growth Partners",
                investor_type="Investment fund",
                budget_range="5-10M EGP",
                status="under_review",
                owner_notes="Needs follow-up on land allocation.",
            ),
            InvestmentInterest(
                opportunity_id=opportunities[2].id,
                investor_id="00000000-0000-0000-0000-000000000005",
                message="Looking to support expansion into nearby farming clusters.",
                contact_name="Investor Five",
                contact_email="investor5@example.com",
                contact_phone="+201000000005",
                company_name="Oasis Capital",
                investor_type="Company",
                budget_range="1-5M EGP",
                status="submitted",
            ),
        ]
        session.add_all(interests)
        session.flush()

        watchlist_entries = [
            InvestmentWatchlist(
                investor_id="00000000-0000-0000-0000-000000000009",
                opportunity_id=opportunities[1].id,
            ),
            InvestmentWatchlist(
                investor_id="00000000-0000-0000-0000-000000000009",
                opportunity_id=opportunities[2].id,
            ),
        ]
        session.add_all(watchlist_entries)
        session.flush()

        for opportunity in opportunities:
            opportunity.interest_count = (
                session.query(InvestmentInterest)
                .filter(
                    InvestmentInterest.opportunity_id == opportunity.id,
                    InvestmentInterest.status != "withdrawn",
                )
                .count()
            )

        session.commit()
    finally:
        session.close()
