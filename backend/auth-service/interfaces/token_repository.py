"""Abstract interface for token repository — Dependency Inversion Principle."""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from datetime import datetime

from models import RefreshToken


class ITokenRepository(ABC):
    """Contract for refresh token data access."""

    @abstractmethod
    async def store(self, token: RefreshToken) -> RefreshToken:
        """Persist a new refresh token record."""
        ...

    @abstractmethod
    async def find_by_hash(self, token_hash: str) -> Optional[RefreshToken]:
        """Find a valid (non-revoked, non-expired) token by its hash."""
        ...

    @abstractmethod
    async def revoke(self, token_hash: str) -> bool:
        """Revoke a refresh token by its hash."""
        ...

    @abstractmethod
    async def revoke_all_for_user(self, user_id: UUID) -> int:
        """Revoke all tokens for a user (e.g., on password change). Returns count."""
        ...
