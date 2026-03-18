"""Repository contract for PointOfInterest."""

from abc import ABC, abstractmethod
from typing import Optional

from models import PointOfInterest


class IPointOfInterestRepository(ABC):

    @abstractmethod
    async def create(self, entity: PointOfInterest) -> PointOfInterest:
        raise NotImplementedError

    @abstractmethod
    async def list(self, status_filter: Optional[str] = None) -> list[PointOfInterest]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[PointOfInterest]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_title(self, title: str) -> Optional[PointOfInterest]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, entity: PointOfInterest) -> PointOfInterest:
        raise NotImplementedError
