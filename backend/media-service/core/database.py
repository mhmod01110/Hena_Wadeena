"""Media service database setup."""

import os
import sys

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from core.config import settings
from shared.core.database import Base, create_db_engine, create_session_factory, ensure_database_exists

engine = create_db_engine(settings.MEDIA_DATABASE_URL, echo=settings.DEBUG)
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
    await ensure_database_exists(settings.MEDIA_DATABASE_URL, echo=settings.DEBUG)
    import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_seed_data)


def _seed_data(sync_conn) -> None:
    from models import MediaAsset

    session = Session(bind=sync_conn)
    try:
        if session.query(MediaAsset).count() > 0:
            return

        rows = [
            MediaAsset(
                title="seed:asset:guide-license",
                status="ready",
                owner_id="00000000-0000-0000-0000-000000000003",
                file_name="guide-license.pdf",
                mime_type="application/pdf",
                size_bytes=245760,
                checksum="seed-guide-license",
                url="https://cdn.hena.local/media/guide-license.pdf",
            ),
            MediaAsset(
                title="seed:asset:merchant-banner",
                status="ready",
                owner_id="00000000-0000-0000-0000-000000000006",
                file_name="merchant-banner.jpg",
                mime_type="image/jpeg",
                size_bytes=384512,
                checksum="seed-merchant-banner",
                url="https://cdn.hena.local/media/merchant-banner.jpg",
            ),
            MediaAsset(
                title="seed:asset:tourism-map",
                status="ready",
                owner_id="00000000-0000-0000-0000-000000000001",
                file_name="tourism-map.png",
                mime_type="image/png",
                size_bytes=512000,
                checksum="seed-tourism-map",
                url="https://cdn.hena.local/media/tourism-map.png",
            ),
        ]

        session.add_all(rows)
        session.commit()
    finally:
        session.close()
