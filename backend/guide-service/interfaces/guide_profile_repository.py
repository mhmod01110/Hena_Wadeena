from __future__ import annotations

"""Repository contract for GuideProfile."""

from abc import ABC, abstractmethod
from typing import Optional

from models import GuideProfile


class IGuideProfileRepository(ABC):

    @abstractmethod
    async def create(self, entity: GuideProfile) -> GuideProfile:
        raise NotImplementedError

    @abstractmethod
    async def list(self, status_filter: Optional[str] = None) -> list[GuideProfile]:
        raise NotImplementedError

    @abstractmethod
    async def list_by_kind(self, entity_kind: str, status_filter: Optional[str] = None) -> list[GuideProfile]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[GuideProfile]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_title(self, title: str) -> Optional[GuideProfile]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, entity: GuideProfile) -> GuideProfile:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, entity: GuideProfile) -> None:
        raise NotImplementedError
