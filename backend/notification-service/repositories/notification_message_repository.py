"""SQLAlchemy repository for NotificationMessage."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from interfaces.notification_message_repository import INotificationMessageRepository
from models import NotificationMessage


class SqlAlchemyNotificationMessageRepository(INotificationMessageRepository):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, entity: NotificationMessage) -> NotificationMessage:
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def list(self, status_filter: Optional[str] = None) -> list[NotificationMessage]:
        query = select(NotificationMessage)
        if status_filter:
            query = query.where(NotificationMessage.status == status_filter)
        query = query.order_by(NotificationMessage.created_at.desc())
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, entity_id: str) -> Optional[NotificationMessage]:
        result = await self._session.execute(select(NotificationMessage).where(NotificationMessage.id == entity_id))
        return result.scalar_one_or_none()

    async def get_by_title(self, title: str) -> Optional[NotificationMessage]:
        result = await self._session.execute(select(NotificationMessage).where(NotificationMessage.title == title))
        return result.scalar_one_or_none()

    async def update(self, entity: NotificationMessage) -> NotificationMessage:
        await self._session.flush()
        await self._session.refresh(entity)
        return entity
