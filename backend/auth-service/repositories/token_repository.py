"""Concrete token repository — SQLAlchemy implementation."""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from interfaces.token_repository import ITokenRepository
from models import RefreshToken


class SqlAlchemyTokenRepository(ITokenRepository):
    """SQLAlchemy implementation of ITokenRepository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def store(self, token: RefreshToken) -> RefreshToken:
        self._session.add(token)
        await self._session.flush()
        await self._session.refresh(token)
        return token

    async def find_by_hash(self, token_hash: str) -> Optional[RefreshToken]:
        result = await self._session.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.expires_at > datetime.now(timezone.utc),
            )
        )
        return result.scalar_one_or_none()

    async def revoke(self, token_hash: str) -> bool:
        record = await self.find_by_hash(token_hash)
        if record:
            record.revoked_at = datetime.now(timezone.utc)
            await self._session.flush()
            return True
        return False

    async def revoke_all_for_user(self, user_id: UUID) -> int:
        now = datetime.now(timezone.utc)
        result = await self._session.execute(
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=now)
        )
        await self._session.flush()
        return result.rowcount
