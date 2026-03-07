"""Concrete auth event repository — SQLAlchemy implementation."""

from sqlalchemy.ext.asyncio import AsyncSession

from interfaces.event_repository import IEventRepository
from models import AuthEvent


class SqlAlchemyEventRepository(IEventRepository):
    """SQLAlchemy implementation of IEventRepository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def log(self, event: AuthEvent) -> AuthEvent:
        self._session.add(event)
        await self._session.flush()
        await self._session.refresh(event)
        return event
