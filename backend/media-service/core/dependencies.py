"""Service dependency providers."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from repositories.media_asset_repository import SqlAlchemyMediaAssetRepository
from services.media_asset_service import MediaAssetService


def get_media_asset_service(
    session: AsyncSession = Depends(get_session),
) -> MediaAssetService:
    repository = SqlAlchemyMediaAssetRepository(session)
    return MediaAssetService(repository)
