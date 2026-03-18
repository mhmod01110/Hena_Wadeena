"""Repository contract for SearchDocument."""

from abc import ABC, abstractmethod
from typing import Optional

from models import SearchDocument


class ISearchDocumentRepository(ABC):

    @abstractmethod
    async def create(self, entity: SearchDocument) -> SearchDocument:
        raise NotImplementedError

    @abstractmethod
    async def list(self, status_filter: Optional[str] = None) -> list[SearchDocument]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[SearchDocument]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_title(self, title: str) -> Optional[SearchDocument]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, entity: SearchDocument) -> SearchDocument:
        raise NotImplementedError
