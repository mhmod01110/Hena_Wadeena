"""Business logic for Listing."""

from typing import Optional

from interfaces.listing_repository import IListingRepository
from models import Listing


class ListingService:

    def __init__(self, repository: IListingRepository):
        self._repository = repository

    async def create_entity(
        self,
        title: str,
        description: Optional[str],
        status: str,
        data: dict,
    ) -> Listing:
        normalized_title = title.strip()
        if not normalized_title:
            raise ValueError("Title cannot be empty")

        existing = await self._repository.get_by_title(normalized_title)
        if existing:
            raise ValueError("Entity with this title already exists")

        entity = Listing(
            title=normalized_title,
            description=description,
            status=status,
            owner_id=data["owner_id"],
            listing_type=data.get("listing_type", "sell"),
            category=data["category"],
            location=data["location"],
            price=float(data["price"]),
            currency=data.get("currency", "EGP"),
            is_verified=bool(data.get("is_verified", False)),
        )
        return await self._repository.create(entity)

    async def list_entities(self, status_filter: Optional[str] = None) -> list[Listing]:
        return await self._repository.list(status_filter=status_filter)

    async def get_entity(self, entity_id: str) -> Optional[Listing]:
        return await self._repository.get_by_id(entity_id)

    async def update_entity(self, entity_id: str, **fields) -> Optional[Listing]:
        entity = await self._repository.get_by_id(entity_id)
        if not entity:
            return None

        title = fields.get("title")
        if title is not None:
            normalized_title = title.strip()
            if not normalized_title:
                raise ValueError("Title cannot be empty")

            existing = await self._repository.get_by_title(normalized_title)
            if existing and str(existing.id) != str(entity.id):
                raise ValueError("Entity with this title already exists")
            entity.title = normalized_title

        for key in ("description", "status"):
            if key in fields and fields[key] is not None:
                setattr(entity, key, fields[key])

        if "data" in fields and fields["data"] is not None:
            patch = fields["data"]
            for key in ("listing_type", "category", "location", "currency"):
                if key in patch and patch[key] is not None:
                    setattr(entity, key, patch[key])
            if "price" in patch and patch["price"] is not None:
                entity.price = float(patch["price"])
            if "is_verified" in patch and patch["is_verified"] is not None:
                entity.is_verified = bool(patch["is_verified"])

        return await self._repository.update(entity)