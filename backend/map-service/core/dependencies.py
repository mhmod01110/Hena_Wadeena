"""Service dependency providers."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from repositories.point_of_interest_repository import SqlAlchemyPointOfInterestRepository
from services.point_of_interest_service import PointOfInterestService


def get_point_of_interest_service(
    session: AsyncSession = Depends(get_session),
) -> PointOfInterestService:
    repository = SqlAlchemyPointOfInterestRepository(session)
    return PointOfInterestService(repository)
