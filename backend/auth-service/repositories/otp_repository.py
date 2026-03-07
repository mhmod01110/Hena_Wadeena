"""Concrete OTP repository — SQLAlchemy implementation."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from interfaces.otp_repository import IOTPRepository
from models import OTPCode
from core.config import settings


class SqlAlchemyOTPRepository(IOTPRepository):
    """SQLAlchemy implementation of IOTPRepository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def store(self, otp: OTPCode) -> OTPCode:
        self._session.add(otp)
        await self._session.flush()
        await self._session.refresh(otp)
        return otp

    async def find_valid(self, target: str, purpose: str, code_hash: str) -> Optional[OTPCode]:
        result = await self._session.execute(
            select(OTPCode).where(
                OTPCode.target == target,
                OTPCode.purpose == purpose,
                OTPCode.code_hash == code_hash,
                OTPCode.used_at.is_(None),
                OTPCode.expires_at > datetime.now(timezone.utc),
                OTPCode.attempts < settings.OTP_MAX_ATTEMPTS,
            )
        )
        return result.scalar_one_or_none()

    async def mark_used(self, otp: OTPCode) -> None:
        otp.used_at = datetime.now(timezone.utc)
        await self._session.flush()

    async def increment_attempts(self, target: str, purpose: str) -> None:
        result = await self._session.execute(
            select(OTPCode).where(
                OTPCode.target == target,
                OTPCode.purpose == purpose,
                OTPCode.used_at.is_(None),
            ).order_by(OTPCode.id.desc()).limit(1)
        )
        latest = result.scalar_one_or_none()
        if latest:
            latest.attempts += 1
            await self._session.flush()
