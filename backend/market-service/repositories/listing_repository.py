"""SQLAlchemy repository for Listing."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from interfaces.listing_repository import IListingRepository
from models import Listing


class SqlAlchemyListingRepository(IListingRepository):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, entity: Listing) -> Listing:
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def list(self, status_filter: Optional[str] = None) -> list[Listing]:
        query = select(Listing)
        if status_filter:
            query = query.where(Listing.status == status_filter)
        query = query.order_by(Listing.created_at.desc())
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, entity_id: str) -> Optional[Listing]:
        result = await self._session.execute(select(Listing).where(Listing.id == entity_id))
        return result.scalar_one_or_none()

    async def get_by_title(self, title: str) -> Optional[Listing]:
        result = await self._session.execute(select(Listing).where(Listing.title == title))
        return result.scalar_one_or_none()

    async def update(self, entity: Listing) -> Listing:
        await self._session.flush()
        await self._session.refresh(entity)
        return entity
