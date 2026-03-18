"""SQLAlchemy repository for MediaAsset."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from interfaces.media_asset_repository import IMediaAssetRepository
from models import MediaAsset


class SqlAlchemyMediaAssetRepository(IMediaAssetRepository):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, entity: MediaAsset) -> MediaAsset:
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def list(self, status_filter: Optional[str] = None) -> list[MediaAsset]:
        query = select(MediaAsset)
        if status_filter:
            query = query.where(MediaAsset.status == status_filter)
        query = query.order_by(MediaAsset.created_at.desc())
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, entity_id: str) -> Optional[MediaAsset]:
        result = await self._session.execute(select(MediaAsset).where(MediaAsset.id == entity_id))
        return result.scalar_one_or_none()

    async def get_by_title(self, title: str) -> Optional[MediaAsset]:
        result = await self._session.execute(select(MediaAsset).where(MediaAsset.title == title))
        return result.scalar_one_or_none()

    async def update(self, entity: MediaAsset) -> MediaAsset:
        await self._session.flush()
        await self._session.refresh(entity)
        return entity
