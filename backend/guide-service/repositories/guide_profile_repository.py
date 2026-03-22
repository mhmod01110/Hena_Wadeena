from __future__ import annotations

"""SQLAlchemy repository for GuideProfile."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from interfaces.guide_profile_repository import IGuideProfileRepository
from models import GuideProfile


class SqlAlchemyGuideProfileRepository(IGuideProfileRepository):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, entity: GuideProfile) -> GuideProfile:
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def list(self, status_filter: Optional[str] = None) -> list[GuideProfile]:
        query = select(GuideProfile)
        if status_filter:
            query = query.where(GuideProfile.status == status_filter)
        query = query.order_by(GuideProfile.created_at.desc())
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def list_by_kind(self, entity_kind: str, status_filter: Optional[str] = None) -> list[GuideProfile]:
        query = select(GuideProfile).where(GuideProfile.entity_kind == entity_kind)
        if status_filter:
            query = query.where(GuideProfile.status == status_filter)
        query = query.order_by(GuideProfile.created_at.desc())
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, entity_id: str) -> Optional[GuideProfile]:
        result = await self._session.execute(select(GuideProfile).where(GuideProfile.id == entity_id))
        return result.scalar_one_or_none()

    async def get_by_title(self, title: str) -> Optional[GuideProfile]:
        result = await self._session.execute(select(GuideProfile).where(GuideProfile.title == title))
        return result.scalar_one_or_none()

    async def update(self, entity: GuideProfile) -> GuideProfile:
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def delete(self, entity: GuideProfile) -> None:
        await self._session.delete(entity)
        await self._session.flush()
