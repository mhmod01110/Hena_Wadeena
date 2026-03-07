"""Abstract interface for user repository."""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from models import User


class IUserRepository(ABC):

    @abstractmethod
    async def create(self, user: User) -> User:
        ...

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        ...

    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]:
        ...

    @abstractmethod
    async def find_by_phone(self, phone: str) -> Optional[User]:
        ...

    @abstractmethod
    async def exists(self, email: Optional[str], phone: Optional[str]) -> bool:
        ...

    @abstractmethod
    async def update(self, user: User) -> User:
        ...
