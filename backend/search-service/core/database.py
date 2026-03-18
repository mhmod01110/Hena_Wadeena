"""Search service database setup."""

import os
import sys

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from core.config import settings
from shared.core.database import Base, create_db_engine, create_session_factory, ensure_database_exists

engine = create_db_engine(settings.SEARCH_DATABASE_URL, echo=settings.DEBUG)
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
    await ensure_database_exists(settings.SEARCH_DATABASE_URL, echo=settings.DEBUG)
    import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_seed_data)


def _seed_data(sync_conn) -> None:
    from models import SearchDocument

    session = Session(bind=sync_conn)
    try:
        if session.query(SearchDocument).count() > 0:
            return

        rows = [
            SearchDocument(
                title="Hibis Temple",
                description="Historic temple in Kharga oasis",
                status="indexed",
                resource_type="attraction",
                resource_id="hibis-temple",
                location="Kharga",
                tags_csv="tourism,heritage,temple",
                url="/tourism/attraction/hibis-temple",
            ),
            SearchDocument(
                title="Ahmed El Sayed",
                description="Licensed desert and heritage guide",
                status="indexed",
                resource_type="guide",
                resource_id="00000000-0000-0000-0000-000000000003",
                location="Kharga",
                tags_csv="guide,tourism,desert",
                url="/guides/00000000-0000-0000-0000-000000000003",
            ),
            SearchDocument(
                title="Green Valley Farms",
                description="Premium dates and olives supplier",
                status="indexed",
                resource_type="supplier",
                resource_id="green-valley-farms",
                location="Kharga",
                tags_csv="market,supplier,agriculture",
                url="/marketplace/supplier/green-valley-farms",
            ),
            SearchDocument(
                title="Integrated Farm Project",
                description="100-acre farm for dates and olives with modern irrigation.",
                status="indexed",
                resource_type="investment",
                resource_id="integrated-farm-project",
                location="Kharga",
                tags_csv="investment,agriculture,roi",
                url="/investment/opportunity/integrated-farm-project",
            ),
            SearchDocument(
                title="Kharga to Assiut Route",
                description="Popular carpool route from Kharga to Assiut",
                status="indexed",
                resource_type="transport",
                resource_id="kharga-assiut",
                location="Kharga",
                tags_csv="transport,carpool,route",
                url="/logistics/route/kharga-assiut",
            ),
        ]

        session.add_all(rows)
        session.commit()
    finally:
        session.close()
