"""Repository contract for Listing."""

from abc import ABC, abstractmethod
from typing import Optional

from models import Listing


class IListingRepository(ABC):

    @abstractmethod
    async def create(self, entity: Listing) -> Listing:
        raise NotImplementedError

    @abstractmethod
    async def list(self, status_filter: Optional[str] = None) -> list[Listing]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[Listing]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_title(self, title: str) -> Optional[Listing]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, entity: Listing) -> Listing:
        raise NotImplementedError
