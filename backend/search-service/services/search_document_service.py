"""Business logic for SearchDocument."""

from typing import Optional

from interfaces.search_document_repository import ISearchDocumentRepository
from models import SearchDocument


def _to_csv(values: list[str] | None) -> str:
    return ",".join(v.strip() for v in (values or []) if v and v.strip())


class SearchDocumentService:

    def __init__(self, repository: ISearchDocumentRepository):
        self._repository = repository

    async def create_entity(
        self,
        title: str,
        description: Optional[str],
        status: str,
        data: dict,
    ) -> SearchDocument:
        normalized_title = title.strip()
        if not normalized_title:
            raise ValueError("Title cannot be empty")

        existing = await self._repository.get_by_title(normalized_title)
        if existing:
            raise ValueError("Entity with this title already exists")

        entity = SearchDocument(
            title=data.get("title", normalized_title),
            description=description,
            status=status,
            resource_type=data["resource_type"],
            resource_id=data["resource_id"],
            location=data.get("location"),
            tags_csv=_to_csv(data.get("tags") or []),
            url=data.get("url"),
        )
        return await self._repository.create(entity)

    async def list_entities(self, status_filter: Optional[str] = None) -> list[SearchDocument]:
        return await self._repository.list(status_filter=status_filter)

    async def get_entity(self, entity_id: str) -> Optional[SearchDocument]:
        return await self._repository.get_by_id(entity_id)

    async def update_entity(self, entity_id: str, **fields) -> Optional[SearchDocument]:
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
            payload = fields["data"]
            for key in ("resource_type", "resource_id", "location", "url"):
                if key in payload and payload[key] is not None:
                    setattr(entity, key, payload[key])
            if "tags" in payload and payload["tags"] is not None:
                entity.tags_csv = _to_csv(payload["tags"])

        return await self._repository.update(entity)