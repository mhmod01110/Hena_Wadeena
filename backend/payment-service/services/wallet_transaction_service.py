"""Business logic for WalletTransaction."""

from typing import Optional

from interfaces.wallet_transaction_repository import IWalletTransactionRepository
from models import WalletTransaction


class WalletTransactionService:

    def __init__(self, repository: IWalletTransactionRepository):
        self._repository = repository

    async def create_entity(
        self,
        *,
        title: str,
        user_id: str,
        tx_type: str,
        direction: str,
        amount: float,
        balance_after: float,
        status: str,
        payment_method: Optional[str] = None,
        description: Optional[str] = None,
        reference_type: Optional[str] = None,
        reference_id: Optional[str] = None,
    ) -> WalletTransaction:
        normalized_title = title.strip()
        if not normalized_title:
            raise ValueError("Title cannot be empty")

        existing = await self._repository.get_by_title(normalized_title)
        if existing:
            raise ValueError("Entity with this title already exists")

        entity = WalletTransaction(
            title=normalized_title,
            status=status,
            user_id=user_id,
            tx_type=tx_type,
            direction=direction,
            amount=amount,
            balance_after=balance_after,
            payment_method=payment_method,
            reference_type=reference_type,
            reference_id=reference_id,
            description=description,
        )
        return await self._repository.create(entity)

    async def list_entities(self, status_filter: Optional[str] = None) -> list[WalletTransaction]:
        return await self._repository.list(status_filter=status_filter)

    async def get_entity(self, entity_id: str) -> Optional[WalletTransaction]:
        return await self._repository.get_by_id(entity_id)

    async def update_entity(self, entity_id: str, **fields) -> Optional[WalletTransaction]:
        entity = await self._repository.get_by_id(entity_id)
        if not entity:
            return None

        for key in (
            "status",
            "description",
            "payment_method",
            "reference_type",
            "reference_id",
            "balance_after",
        ):
            if key in fields and fields[key] is not None:
                setattr(entity, key, fields[key])

        return await self._repository.update(entity)
