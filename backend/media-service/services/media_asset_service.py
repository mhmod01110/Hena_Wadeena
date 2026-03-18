"""Business logic for MediaAsset."""

from typing import Optional

from interfaces.media_asset_repository import IMediaAssetRepository
from models import MediaAsset


class MediaAssetService:

    def __init__(self, repository: IMediaAssetRepository):
        self._repository = repository

    async def create_entity(
        self,
        *,
        title: str,
        owner_id: str,
        file_name: str,
        mime_type: str,
        size_bytes: int,
        status: str = "pending",
        checksum: Optional[str] = None,
        url: Optional[str] = None,
    ) -> MediaAsset:
        normalized_title = title.strip()
        if not normalized_title:
            raise ValueError("Title cannot be empty")

        existing = await self._repository.get_by_title(normalized_title)
        if existing:
            raise ValueError("Entity with this title already exists")

        entity = MediaAsset(
            title=normalized_title,
            status=status,
            owner_id=owner_id,
            file_name=file_name,
            mime_type=mime_type,
            size_bytes=size_bytes,
            checksum=checksum,
            url=url,
        )
        return await self._repository.create(entity)

    async def list_entities(self, status_filter: Optional[str] = None) -> list[MediaAsset]:
        return await self._repository.list(status_filter=status_filter)

    async def get_entity(self, entity_id: str) -> Optional[MediaAsset]:
        return await self._repository.get_by_id(entity_id)

    async def update_entity(self, entity_id: str, **fields) -> Optional[MediaAsset]:
        entity = await self._repository.get_by_id(entity_id)
        if not entity:
            return None

        for key in ("status", "url", "checksum"):
            if key in fields and fields[key] is not None:
                setattr(entity, key, fields[key])

        return await self._repository.update(entity)
