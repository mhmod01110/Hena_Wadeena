"""Auth service — pure business logic, no HTTP concerns."""

import sys
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared.utils.jwt import create_access_token, create_refresh_token_value
from shared.utils.security import hash_password, verify_password, hash_token

from interfaces.token_repository import ITokenRepository
from interfaces.event_repository import IEventRepository
from models import RefreshToken, AuthEvent
from core.config import settings


class AuthService:
    """
    Encapsulates all authentication business logic.
    Depends on repository interfaces (DIP), never on HTTP/FastAPI.
    """

    def __init__(
        self,
        token_repo: ITokenRepository,
        event_repo: IEventRepository,
    ):
        self._token_repo = token_repo
        self._event_repo = event_repo

    # ── Password helpers ─────────────────────────────────────────────────

    @staticmethod
    def hash_password(password: str) -> str:
        return hash_password(password)

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        return verify_password(plain, hashed)

    # ── Token issuance ───────────────────────────────────────────────────

    async def issue_tokens(
        self,
        user_id: str,
        role: str,
        device_id: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> dict:
        """Issue access + refresh token pair."""
        access_token = create_access_token(
            user_id=user_id,
            role=role,
            secret_key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
            expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )

        raw_refresh = create_refresh_token_value()
        refresh_record = RefreshToken(
            user_id=uuid.UUID(user_id),
            token_hash=hash_token(raw_refresh),
            device_id=device_id,
            ip_address=ip_address,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        await self._token_repo.store(refresh_record)

        return {
            "access_token": access_token,
            "refresh_token": raw_refresh,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    # ── Refresh ──────────────────────────────────────────────────────────

    async def validate_refresh_token(self, raw_token: str) -> Optional[RefreshToken]:
        """Validate a refresh token. Returns the DB record or None."""
        return await self._token_repo.find_by_hash(hash_token(raw_token))

    async def rotate_refresh_token(
        self,
        old_raw_token: str,
        user_id: str,
        role: str,
        ip_address: Optional[str] = None,
    ) -> dict:
        """Revoke old token, issue new pair (token rotation)."""
        await self._token_repo.revoke(hash_token(old_raw_token))
        return await self.issue_tokens(user_id, role, ip_address=ip_address)

    # ── Logout ───────────────────────────────────────────────────────────

    async def revoke_token(self, raw_token: str) -> bool:
        """Revoke a single refresh token."""
        return await self._token_repo.revoke(hash_token(raw_token))

    # ── Audit ────────────────────────────────────────────────────────────

    async def log_event(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """Log an auth audit event."""
        event = AuthEvent(
            user_id=uuid.UUID(user_id) if user_id else None,
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await self._event_repo.log(event)
