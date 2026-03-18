"""Business logic for GuideProfile."""

from typing import Optional

from interfaces.guide_profile_repository import IGuideProfileRepository
from models import GuideProfile


def _to_csv(values: list[str] | None) -> str:
    return ",".join(v.strip() for v in (values or []) if v and v.strip())


class GuideProfileService:

    def __init__(self, repository: IGuideProfileRepository):
        self._repository = repository

    @staticmethod
    def _apply_payload(entity: GuideProfile, payload: dict) -> None:
        kind = str(payload.get("type") or entity.entity_kind or "guide_profile")
        entity.entity_kind = kind

        if kind == "guide_profile":
            entity.user_id = payload.get("user_id", entity.user_id)
            entity.display_name = payload.get("display_name", entity.display_name)
            entity.bio = payload.get("bio", entity.bio)
            if "languages" in payload:
                entity.languages_csv = _to_csv(payload.get("languages") or [])
            if "specialties" in payload:
                entity.specialties_csv = _to_csv(payload.get("specialties") or [])
            if payload.get("base_price") is not None:
                entity.base_price = float(payload["base_price"])
            if payload.get("active") is not None:
                entity.active = bool(payload["active"])
            if payload.get("verified") is not None:
                entity.verified = bool(payload["verified"])
        elif kind == "booking":
            entity.guide_profile_id = payload.get("guide_profile_id", entity.guide_profile_id)
            entity.guide_user_id = payload.get("guide_user_id", entity.guide_user_id)
            entity.tourist_id = payload.get("tourist_id", entity.tourist_id)
            entity.booking_date = payload.get("booking_date", entity.booking_date)
            entity.start_time = payload.get("start_time", entity.start_time)
            if payload.get("people_count") is not None:
                entity.people_count = int(payload["people_count"])
            if payload.get("total_price") is not None:
                entity.total_price = float(payload["total_price"])
            entity.notes = payload.get("notes", entity.notes)

    async def create_entity(
        self,
        title: str,
        description: Optional[str],
        status: str,
        data: dict,
    ) -> GuideProfile:
        normalized_title = title.strip()
        if not normalized_title:
            raise ValueError("Title cannot be empty")

        existing = await self._repository.get_by_title(normalized_title)
        if existing:
            raise ValueError("Entity with this title already exists")

        entity = GuideProfile(
            title=normalized_title,
            description=description,
            status=status,
            entity_kind=str(data.get("type") or "guide_profile"),
        )
        self._apply_payload(entity, data)
        return await self._repository.create(entity)

    async def list_entities(self, status_filter: Optional[str] = None) -> list[GuideProfile]:
        return await self._repository.list(status_filter=status_filter)

    async def get_entity(self, entity_id: str) -> Optional[GuideProfile]:
        return await self._repository.get_by_id(entity_id)

    async def update_entity(self, entity_id: str, **fields) -> Optional[GuideProfile]:
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