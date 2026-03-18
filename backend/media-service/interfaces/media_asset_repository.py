"""Repository contract for MediaAsset."""

from abc import ABC, abstractmethod
from typing import Optional

from models import MediaAsset


class IMediaAssetRepository(ABC):

    @abstractmethod
    async def create(self, entity: MediaAsset) -> MediaAsset:
        raise NotImplementedError

    @abstractmethod
    async def list(self, status_filter: Optional[str] = None) -> list[MediaAsset]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[MediaAsset]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_title(self, title: str) -> Optional[MediaAsset]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, entity: MediaAsset) -> MediaAsset:
        raise NotImplementedError
