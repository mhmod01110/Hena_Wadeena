"""Repository contract for NotificationMessage."""

from abc import ABC, abstractmethod
from typing import Optional

from models import NotificationMessage


class INotificationMessageRepository(ABC):

    @abstractmethod
    async def create(self, entity: NotificationMessage) -> NotificationMessage:
        raise NotImplementedError

    @abstractmethod
    async def list(self, status_filter: Optional[str] = None) -> list[NotificationMessage]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[NotificationMessage]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_title(self, title: str) -> Optional[NotificationMessage]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, entity: NotificationMessage) -> NotificationMessage:
        raise NotImplementedError
