"""Abstract interface for OTP repository."""

from abc import ABC, abstractmethod
from typing import Optional

from models import OTPCode


class IOTPRepository(ABC):
    """Contract for OTP data access."""

    @abstractmethod
    async def store(self, otp: OTPCode) -> OTPCode:
        """Persist a new OTP code."""
        ...

    @abstractmethod
    async def find_valid(self, target: str, purpose: str, code_hash: str) -> Optional[OTPCode]:
        """Find a valid (unused, non-expired, under max attempts) OTP."""
        ...

    @abstractmethod
    async def mark_used(self, otp: OTPCode) -> None:
        """Mark an OTP as used."""
        ...

    @abstractmethod
    async def increment_attempts(self, target: str, purpose: str) -> None:
        """Increment attempt counter on the latest OTP for this target."""
        ...
