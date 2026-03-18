"""Business logic for PointOfInterest."""

from typing import Optional

from interfaces.point_of_interest_repository import IPointOfInterestRepository
from models import PointOfInterest


class PointOfInterestService:

    def __init__(self, repository: IPointOfInterestRepository):
        self._repository = repository

    @staticmethod
    def _apply_payload(entity: PointOfInterest, payload: dict) -> None:
        entity_type = str(payload.get("type") or entity.entity_kind or "poi")
        entity.entity_kind = entity_type
        entity.created_by = payload.get("created_by", entity.created_by)

        if entity_type == "poi":
            entity.name_ar = payload.get("name_ar", entity.name_ar)
            entity.name_en = payload.get("name_en", entity.name_en)
            entity.category = payload.get("category", entity.category)
            entity.address = payload.get("address", entity.address)
            entity.lat = payload.get("lat", entity.lat)
            entity.lng = payload.get("lng", entity.lng)
            entity.phone = payload.get("phone", entity.phone)
        elif entity_type == "carpool_ride":
            entity.driver_id = payload.get("driver_id", entity.driver_id)
            entity.origin_name = payload.get("origin_name", entity.origin_name)
            entity.destination_name = payload.get("destination_name", entity.destination_name)
            entity.departure_time = payload.get("departure_time", entity.departure_time)
            entity.seats_total = payload.get("seats_total", entity.seats_total)
            entity.seats_taken = payload.get("seats_taken", entity.seats_taken)
            entity.price_per_seat = payload.get("price_per_seat", entity.price_per_seat)
            entity.notes = payload.get("notes", entity.notes)

    async def create_entity(
        self,
        title: str,
        description: Optional[str],
        status: str,
        data: dict,
    ) -> PointOfInterest:
        normalized_title = title.strip()
        if not normalized_title:
            raise ValueError("Title cannot be empty")

        existing = await self._repository.get_by_title(normalized_title)
        if existing:
            raise ValueError("Entity with this title already exists")

        entity = PointOfInterest(
            title=normalized_title,
            description=description,
            status=status,
            entity_kind=str(data.get("type") or "poi"),
        )
        self._apply_payload(entity, data)
        return await self._repository.create(entity)

    async def list_entities(self, status_filter: Optional[str] = None) -> list[PointOfInterest]:
        return await self._repository.list(status_filter=status_filter)

    async def get_entity(self, entity_id: str) -> Optional[PointOfInterest]:
        return await self._repository.get_by_id(entity_id)

    async def update_entity(self, entity_id: str, **fields) -> Optional[PointOfInterest]:
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
            self._apply_payload(entity, fields["data"])

        return await self._repository.update(entity)