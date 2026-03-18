"""SQLAlchemy repository for SearchDocument."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from interfaces.search_document_repository import ISearchDocumentRepository
from models import SearchDocument


class SqlAlchemySearchDocumentRepository(ISearchDocumentRepository):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, entity: SearchDocument) -> SearchDocument:
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def list(self, status_filter: Optional[str] = None) -> list[SearchDocument]:
        query = select(SearchDocument)
        if status_filter:
            query = query.where(SearchDocument.status == status_filter)
        query = query.order_by(SearchDocument.created_at.desc())
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, entity_id: str) -> Optional[SearchDocument]:
        result = await self._session.execute(select(SearchDocument).where(SearchDocument.id == entity_id))
        return result.scalar_one_or_none()

    async def get_by_title(self, title: str) -> Optional[SearchDocument]:
        result = await self._session.execute(select(SearchDocument).where(SearchDocument.title == title))
        return result.scalar_one_or_none()

    async def update(self, entity: SearchDocument) -> SearchDocument:
        await self._session.flush()
        await self._session.refresh(entity)
        return entity
