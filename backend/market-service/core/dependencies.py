"""Service dependency providers."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from repositories.listing_repository import SqlAlchemyListingRepository
from services.listing_service import ListingService


def get_listing_service(
    session: AsyncSession = Depends(get_session),
) -> ListingService:
    repository = SqlAlchemyListingRepository(session)
    return ListingService(repository)
