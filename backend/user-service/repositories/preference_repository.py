"""Concrete preference repository."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from interfaces.preference_repository import IPreferenceRepository
from models import UserPreference


class SqlAlchemyPreferenceRepository(IPreferenceRepository):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get(self, user_id: str) -> Optional[UserPreference]:
        result = await self._session.execute(
            select(UserPreference).where(UserPreference.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def upsert(self, pref: UserPreference) -> UserPreference:
        existing = await self.get(pref.user_id)
        if existing:
            existing.notify_push = pref.notify_push
            existing.notify_email = pref.notify_email
            existing.notify_sms = pref.notify_sms
            existing.preferred_areas = pref.preferred_areas
            existing.interests = pref.interests
            await self._session.flush()
            await self._session.refresh(existing)
            return existing
        else:
            self._session.add(pref)
            await self._session.flush()
            await self._session.refresh(pref)
            return pref
