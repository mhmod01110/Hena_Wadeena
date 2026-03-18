"""HTTP controller for investment opportunities and interests."""

from __future__ import annotations

from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from core.dependencies import get_opportunity_service
from schemas.requests import OpportunityCreate, OpportunityUpdate, InterestCreate
from schemas.responses import OpportunityResponse, InterestResponse
from services.opportunity_service import OpportunityService


router = APIRouter()


CREATOR_ROLES = {"investor", "merchant", "admin", "super_admin"}
REVIEW_ROLES = {"reviewer", "admin", "super_admin"}


def _envelope(data: Any = None, meta: Optional[dict] = None, error: Optional[str] = None, success: bool = True) -> dict:
    return {"success": success, "data": data, "meta": meta, "error": error}


def _user_id(request: Request) -> str:
    uid = request.headers.get("X-User-Id")
    if not uid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")
    return uid


def _role(request: Request) -> str:
    return request.headers.get("X-User-Role", "tourist")


def _to_opportunity(entity) -> OpportunityResponse:
    return OpportunityResponse(
        id=str(entity.id),
        owner_id=entity.owner_id or "unknown",
        title=entity.title,
        category=entity.category or "",
        location=entity.location or "",
        min_investment=float(entity.min_investment or 0),
        max_investment=float(entity.max_investment or 0),
        expected_roi=entity.expected_roi or "",
        description=entity.description or "",
        status=entity.status,
        is_verified=bool(entity.is_verified),
        created_at=entity.created_at,
    )


def _to_interest(entity) -> InterestResponse:
    return InterestResponse(
        id=str(entity.id),
        opportunity_id=entity.opportunity_id or "",
        investor_id=entity.investor_id or "",
        message=entity.message or "",
        status=entity.status,
        created_at=entity.created_at,
    )


@router.post("/api/v1/investments/opportunities", status_code=status.HTTP_201_CREATED)
async def create_opportunity(
    body: OpportunityCreate,
    request: Request,
    service: OpportunityService = Depends(get_opportunity_service),
):
    role = _role(request)
    if role not in CREATOR_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role not allowed to create opportunities")

    payload = body.model_dump()
    payload.update({
        "type": "opportunity",
        "owner_id": _user_id(request),
        "is_verified": role in REVIEW_ROLES,
    })

    entity = await service.create_entity(
        title=f"opportunity:{body.title}:{uuid4()}",
        description=body.description,
        status="open",
        data=payload,
    )
    return _envelope(_to_opportunity(entity).model_dump())


@router.get("/api/v1/investments/opportunities")
async def list_opportunities(
    category: Optional[str] = Query(default=None),
    location: Optional[str] = Query(default=None),
    status_filter: Optional[str] = Query(default="open", alias="status"),
    service: OpportunityService = Depends(get_opportunity_service),
):
    entities = await service.list_entities(status_filter=status_filter)
    items = []
    for entity in entities:
        if entity.entity_kind != "opportunity":
            continue
        if category and entity.category != category:
            continue
        if location and location.lower() not in str(entity.location or "").lower():
            continue
        items.append(_to_opportunity(entity))

    return _envelope([item.model_dump() for item in items], meta={"total": len(items)})


@router.get("/api/v1/investments/opportunities/{entity_id}")
async def get_opportunity(
    entity_id: str,
    service: OpportunityService = Depends(get_opportunity_service),
):
    entity = await service.get_entity(entity_id)
    if not entity or entity.entity_kind != "opportunity":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")
    return _envelope(_to_opportunity(entity).model_dump())


@router.patch("/api/v1/investments/opportunities/{entity_id}")
async def update_opportunity(
    entity_id: str,
    body: OpportunityUpdate,
    request: Request,
    service: OpportunityService = Depends(get_opportunity_service),
):
    entity = await service.get_entity(entity_id)
    if not entity or entity.entity_kind != "opportunity":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    role = _role(request)
    user_id = _user_id(request)
    if role not in REVIEW_ROLES and entity.owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to update this opportunity")

    patch = body.model_dump(exclude_unset=True)
    patch["type"] = "opportunity"
    status_value = entity.status
    if "status" in patch:
        status_value = patch.pop("status")

    updated = await service.update_entity(entity_id, data=patch, status=status_value)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    return _envelope(_to_opportunity(updated).model_dump())


@router.post("/api/v1/investments/interests", status_code=status.HTTP_201_CREATED)
async def create_interest(
    body: InterestCreate,
    request: Request,
    service: OpportunityService = Depends(get_opportunity_service),
):
    role = _role(request)
    if role not in CREATOR_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role not allowed to submit interest")

    opportunity = await service.get_entity(body.opportunity_id)
    if not opportunity or opportunity.entity_kind != "opportunity":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    payload = {
        "type": "interest",
        "opportunity_id": body.opportunity_id,
        "investor_id": _user_id(request),
        "message": body.message,
    }

    entity = await service.create_entity(
        title=f"interest:{body.opportunity_id}:{_user_id(request)}:{uuid4()}",
        description=body.message,
        status="submitted",
        data=payload,
    )
    return _envelope(_to_interest(entity).model_dump())


@router.get("/api/v1/investments/interests")
async def list_interests(
    request: Request,
    opportunity_id: Optional[str] = None,
    service: OpportunityService = Depends(get_opportunity_service),
):
    uid = _user_id(request)
    role = _role(request)

    entities = await service.list_entities()
    items = []
    for entity in entities:
        if entity.entity_kind != "interest":
            continue
        if opportunity_id and entity.opportunity_id != opportunity_id:
            continue
        if role not in REVIEW_ROLES and entity.investor_id != uid:
            continue
        items.append(_to_interest(entity))

    return _envelope([item.model_dump() for item in items], meta={"total": len(items)})