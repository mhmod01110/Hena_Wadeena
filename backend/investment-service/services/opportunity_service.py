"""Business logic for Opportunity."""

from typing import Optional

from interfaces.opportunity_repository import IOpportunityRepository
from models import Opportunity


class OpportunityService:

    def __init__(self, repository: IOpportunityRepository):
        self._repository = repository

    @staticmethod
    def _apply_payload(entity: Opportunity, payload: dict) -> None:
        kind = str(payload.get("type") or entity.entity_kind or "opportunity")
        entity.entity_kind = kind

        if kind == "opportunity":
            entity.owner_id = payload.get("owner_id", entity.owner_id)
            entity.category = payload.get("category", entity.category)
            entity.location = payload.get("location", entity.location)
            if payload.get("min_investment") is not None:
                entity.min_investment = float(payload["min_investment"])
            if payload.get("max_investment") is not None:
                entity.max_investment = float(payload["max_investment"])
            entity.expected_roi = payload.get("expected_roi", entity.expected_roi)
            if payload.get("is_verified") is not None:
                entity.is_verified = bool(payload["is_verified"])
        elif kind == "interest":
            entity.opportunity_id = payload.get("opportunity_id", entity.opportunity_id)
            entity.investor_id = payload.get("investor_id", entity.investor_id)
            entity.message = payload.get("message", entity.message)

    async def create_entity(
        self,
        title: str,
        description: Optional[str],
        status: str,
        data: dict,
    ) -> Opportunity:
        normalized_title = title.strip()
        if not normalized_title:
            raise ValueError("Title cannot be empty")

        existing = await self._repository.get_by_title(normalized_title)
        if existing:
            raise ValueError("Entity with this title already exists")

        entity = Opportunity(
            title=normalized_title,
            description=description,
            status=status,
            entity_kind=str(data.get("type") or "opportunity"),
        )
        self._apply_payload(entity, data)
        return await self._repository.create(entity)

    async def list_entities(self, status_filter: Optional[str] = None) -> list[Opportunity]:
        return await self._repository.list(status_filter=status_filter)

    async def get_entity(self, entity_id: str) -> Optional[Opportunity]:
        return await self._repository.get_by_id(entity_id)

    async def update_entity(self, entity_id: str, **fields) -> Optional[Opportunity]:
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