"""Abstract interface for auth event repository."""

from abc import ABC, abstractmethod

from models import AuthEvent


class IEventRepository(ABC):
    """Contract for auth audit event data access."""

    @abstractmethod
    async def log(self, event: AuthEvent) -> AuthEvent:
        """Persist an audit event."""
        ...
