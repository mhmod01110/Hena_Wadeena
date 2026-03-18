"""SQLAlchemy repository for WalletTransaction."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from interfaces.wallet_transaction_repository import IWalletTransactionRepository
from models import WalletTransaction


class SqlAlchemyWalletTransactionRepository(IWalletTransactionRepository):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, entity: WalletTransaction) -> WalletTransaction:
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def list(self, status_filter: Optional[str] = None) -> list[WalletTransaction]:
        query = select(WalletTransaction)
        if status_filter:
            query = query.where(WalletTransaction.status == status_filter)
        query = query.order_by(WalletTransaction.created_at.desc())
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, entity_id: str) -> Optional[WalletTransaction]:
        result = await self._session.execute(select(WalletTransaction).where(WalletTransaction.id == entity_id))
        return result.scalar_one_or_none()

    async def get_by_title(self, title: str) -> Optional[WalletTransaction]:
        result = await self._session.execute(select(WalletTransaction).where(WalletTransaction.title == title))
        return result.scalar_one_or_none()

    async def update(self, entity: WalletTransaction) -> WalletTransaction:
        await self._session.flush()
        await self._session.refresh(entity)
        return entity
