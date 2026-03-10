"""Abstract interface for preference repository."""

from abc import ABC, abstractmethod
from typing import Optional

from models import UserPreference


class IPreferenceRepository(ABC):

    @abstractmethod
    async def get(self, user_id: str) -> Optional[UserPreference]:
        ...

    @abstractmethod
    async def upsert(self, pref: UserPreference) -> UserPreference:
        ...
