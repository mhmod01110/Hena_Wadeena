"""Concrete user repository."""

from typing import Optional
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from interfaces.user_repository import IUserRepository
from models import User


class SqlAlchemyUserRepository(IUserRepository):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, user: User) -> User:
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def get_by_id(self, user_id: str) -> Optional[User]:
        result = await self._session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def find_by_email(self, email: str) -> Optional[User]:
        result = await self._session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def find_by_phone(self, phone: str) -> Optional[User]:
        result = await self._session.execute(select(User).where(User.phone == phone))
        return result.scalar_one_or_none()

    async def exists(self, email: Optional[str], phone: Optional[str]) -> bool:
        conditions = []
        if email:
            conditions.append(User.email == email)
        if phone:
            conditions.append(User.phone == phone)
        if not conditions:
            return False
        result = await self._session.execute(select(User).where(or_(*conditions)))
        return result.scalar_one_or_none() is not None

    async def update(self, user: User) -> User:
        await self._session.flush()
        await self._session.refresh(user)
        return user
