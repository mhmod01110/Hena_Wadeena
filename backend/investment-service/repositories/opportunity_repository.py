"""SQLAlchemy repository for Opportunity."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from interfaces.opportunity_repository import IOpportunityRepository
from models import Opportunity


class SqlAlchemyOpportunityRepository(IOpportunityRepository):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, entity: Opportunity) -> Opportunity:
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def list(self, status_filter: Optional[str] = None) -> list[Opportunity]:
        query = select(Opportunity)
        if status_filter:
            query = query.where(Opportunity.status == status_filter)
        query = query.order_by(Opportunity.created_at.desc())
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, entity_id: str) -> Optional[Opportunity]:
        result = await self._session.execute(select(Opportunity).where(Opportunity.id == entity_id))
        return result.scalar_one_or_none()

    async def get_by_title(self, title: str) -> Optional[Opportunity]:
        result = await self._session.execute(select(Opportunity).where(Opportunity.title == title))
        return result.scalar_one_or_none()

    async def update(self, entity: Opportunity) -> Opportunity:
        await self._session.flush()
        await self._session.refresh(entity)
        return entity
