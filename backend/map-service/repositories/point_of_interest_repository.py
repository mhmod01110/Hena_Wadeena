"""SQLAlchemy repository for PointOfInterest."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from interfaces.point_of_interest_repository import IPointOfInterestRepository
from models import PointOfInterest


class SqlAlchemyPointOfInterestRepository(IPointOfInterestRepository):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, entity: PointOfInterest) -> PointOfInterest:
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def list(self, status_filter: Optional[str] = None) -> list[PointOfInterest]:
        query = select(PointOfInterest)
        if status_filter:
            query = query.where(PointOfInterest.status == status_filter)
        query = query.order_by(PointOfInterest.created_at.desc())
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, entity_id: str) -> Optional[PointOfInterest]:
        result = await self._session.execute(select(PointOfInterest).where(PointOfInterest.id == entity_id))
        return result.scalar_one_or_none()

    async def get_by_title(self, title: str) -> Optional[PointOfInterest]:
        result = await self._session.execute(select(PointOfInterest).where(PointOfInterest.title == title))
        return result.scalar_one_or_none()

    async def update(self, entity: PointOfInterest) -> PointOfInterest:
        await self._session.flush()
        await self._session.refresh(entity)
        return entity
