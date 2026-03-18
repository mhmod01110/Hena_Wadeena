"""Service dependency providers."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from repositories.guide_profile_repository import SqlAlchemyGuideProfileRepository
from services.guide_profile_service import GuideProfileService


def get_guide_profile_service(
    session: AsyncSession = Depends(get_session),
) -> GuideProfileService:
    repository = SqlAlchemyGuideProfileRepository(session)
    return GuideProfileService(repository)
