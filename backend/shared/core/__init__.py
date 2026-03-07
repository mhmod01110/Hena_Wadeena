"""Abstract base repository — Repository Pattern."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, Type
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class IRepository(ABC, Generic[T]):
    """Interface for all repositories. Defines the contract for data access."""

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[T]:
        ...

    @abstractmethod
    async def create(self, entity: T) -> T:
        ...

    @abstractmethod
    async def update(self, entity: T) -> T:
        ...

    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        ...


class BaseRepository(IRepository[T]):
    """
    Concrete base repository using SQLAlchemy async session.
    Subclasses set `model` to their SQLAlchemy model class.
    """

    model: Type[T]

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, id: UUID) -> Optional[T]:
        result = await self._session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def create(self, entity: T) -> T:
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def update(self, entity: T) -> T:
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def delete(self, id: UUID) -> bool:
        entity = await self.get_by_id(id)
        if entity:
            await self._session.delete(entity)
            await self._session.flush()
            return True
        return False
