"""Concrete KYC repository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from interfaces.kyc_repository import IKYCRepository
from models import UserKYC


class SqlAlchemyKYCRepository(IKYCRepository):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, kyc: UserKYC) -> UserKYC:
        self._session.add(kyc)
        await self._session.flush()
        await self._session.refresh(kyc)
        return kyc

    async def get_by_user_id(self, user_id: UUID) -> list[UserKYC]:
        result = await self._session.execute(
            select(UserKYC).where(UserKYC.user_id == user_id)
        )
        return list(result.scalars().all())
