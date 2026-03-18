"""Repository contract for WalletTransaction."""

from abc import ABC, abstractmethod
from typing import Optional

from models import WalletTransaction


class IWalletTransactionRepository(ABC):

    @abstractmethod
    async def create(self, entity: WalletTransaction) -> WalletTransaction:
        raise NotImplementedError

    @abstractmethod
    async def list(self, status_filter: Optional[str] = None) -> list[WalletTransaction]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[WalletTransaction]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_title(self, title: str) -> Optional[WalletTransaction]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, entity: WalletTransaction) -> WalletTransaction:
        raise NotImplementedError
