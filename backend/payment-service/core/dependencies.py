"""Service dependency providers."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from repositories.wallet_transaction_repository import SqlAlchemyWalletTransactionRepository
from services.wallet_transaction_service import WalletTransactionService


def get_wallet_transaction_service(
    session: AsyncSession = Depends(get_session),
) -> WalletTransactionService:
    repository = SqlAlchemyWalletTransactionRepository(session)
    return WalletTransactionService(repository)
