"""HTTP controller for search indexing and querying."""

from __future__ import annotations

from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from core.dependencies import get_search_document_service
from schemas.requests import SearchDocumentCreate
from schemas.responses import SearchDocumentResponse
from services.search_document_service import SearchDocumentService


router = APIRouter()


def _envelope(data: Any = None, meta: Optional[dict] = None, error: Optional[str] = None, success: bool = True) -> dict:
    return {"success": success, "data": data, "meta": meta, "error": error}


def _role(request: Request) -> str:
    return request.headers.get("X-User-Role", "tourist")


def _parse_tags(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _to_doc(entity, score: float | None = None) -> SearchDocumentResponse:
    return SearchDocumentResponse(
        id=str(entity.id),
        resource_type=entity.resource_type,
        resource_id=entity.resource_id,
        title=entity.title,
        description=entity.description or "",
        location=entity.location,
        tags=_parse_tags(entity.tags_csv),
        url=entity.url,
        score=score,
        created_at=entity.created_at,
    )


@router.post("/api/v1/search/index", status_code=status.HTTP_201_CREATED)
async def index_document(
    body: SearchDocumentCreate,
    request: Request,
    service: SearchDocumentService = Depends(get_search_document_service),
):
    if _role(request) not in ("admin", "super_admin", "reviewer"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")

    payload = body.model_dump()

    entity = await service.create_entity(
        title=f"doc:{body.resource_type}:{body.resource_id}:{uuid4()}",
        description=body.description,
        status="indexed",
        data=payload,
    )
    return _envelope(_to_doc(entity).model_dump())


@router.get("/api/v1/search")
async def search(
    q: str = Query(default="", max_length=100),
    resource_type: Optional[str] = Query(default=None),
    location: Optional[str] = Query(default=None),
    tags: Optional[str] = Query(default=None, description="Comma-separated tags"),
    limit: int = Query(default=20, ge=1, le=100),
    service: SearchDocumentService = Depends(get_search_document_service),
):
    entities = await service.list_entities()
    tag_set = {tag.strip().lower() for tag in tags.split(",")} if tags else set()

    scored: list[tuple[float, Any]] = []
    query = q.lower().strip()

    for entity in entities:
        if resource_type and entity.resource_type != resource_type:
            continue
        if location and location.lower() not in str(entity.location or "").lower():
            continue

        doc_tags = {str(tag).lower() for tag in _parse_tags(entity.tags_csv)}
        if tag_set and not tag_set.issubset(doc_tags):
            continue

        title = str(entity.title or "")
        description = str(entity.description or "")

        score = 0.0
        if query:
            if query in title.lower():
                score += 3.0
            if query in description.lower():
                score += 1.5
            score += sum(0.5 for word in query.split() if word and word in (title + " " + description).lower())
        else:
            score = 1.0

        scored.append((score, entity))

    scored.sort(key=lambda item: item[0], reverse=True)
    top = scored[:limit]
    result = [_to_doc(entity, score=round(score, 3)).model_dump() for score, entity in top]

    return _envelope(result, meta={"total": len(result), "query": q, "limit": limit})