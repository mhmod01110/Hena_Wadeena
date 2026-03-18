"""Repository contract for Opportunity."""

from abc import ABC, abstractmethod
from typing import Optional

from models import Opportunity


class IOpportunityRepository(ABC):

    @abstractmethod
    async def create(self, entity: Opportunity) -> Opportunity:
        raise NotImplementedError

    @abstractmethod
    async def list(self, status_filter: Optional[str] = None) -> list[Opportunity]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[Opportunity]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_title(self, title: str) -> Optional[Opportunity]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, entity: Opportunity) -> Opportunity:
        raise NotImplementedError
