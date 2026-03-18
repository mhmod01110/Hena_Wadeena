"""HTTP controller for market listings and price insights."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from core.dependencies import get_listing_service
from schemas.requests import ListingCreate, ListingUpdate
from schemas.responses import ListingResponse, PriceInsightResponse
from services.listing_service import ListingService


router = APIRouter()


ALLOWED_CREATOR_ROLES = {"investor", "local_citizen", "merchant", "admin", "super_admin"}


def _envelope(data: Any = None, meta: Optional[dict] = None, error: Optional[str] = None, success: bool = True) -> dict:
    return {"success": success, "data": data, "meta": meta, "error": error}


def _user_id(request: Request) -> str:
    uid = request.headers.get("X-User-Id")
    if not uid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")
    return uid


def _user_role(request: Request) -> str:
    return request.headers.get("X-User-Role", "tourist")


def _to_listing_response(entity) -> ListingResponse:
    return ListingResponse(
        id=str(entity.id),
        owner_id=entity.owner_id,
        title=entity.title,
        listing_type=entity.listing_type,
        category=entity.category,
        location=entity.location,
        price=float(entity.price),
        currency=entity.currency,
        description=entity.description,
        status=entity.status,
        is_verified=bool(entity.is_verified),
        created_at=entity.created_at,
    )


@router.post("/api/v1/market/listings", status_code=status.HTTP_201_CREATED)
@router.post("/api/v1/listings", status_code=status.HTTP_201_CREATED)
async def create_listing(
    body: ListingCreate,
    request: Request,
    service: ListingService = Depends(get_listing_service),
):
    role = _user_role(request)
    if role not in ALLOWED_CREATOR_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role not allowed to create listings")

    payload = body.model_dump()
    payload["owner_id"] = _user_id(request)
    payload["is_verified"] = role in ("admin", "super_admin", "reviewer")

    entity = await service.create_entity(
        title=f"listing:{body.title}:{uuid4()}",
        description=body.description,
        status="active",
        data=payload,
    )
    return _envelope(_to_listing_response(entity).model_dump())


@router.get("/api/v1/market/listings")
@router.get("/api/v1/listings")
async def list_listings(
    category: Optional[str] = Query(default=None),
    location: Optional[str] = Query(default=None),
    listing_type: Optional[str] = Query(default=None),
    status_filter: Optional[str] = Query(default="active", alias="status"),
    service: ListingService = Depends(get_listing_service),
):
    entities = await service.list_entities(status_filter=status_filter)
    listings = []
    for entity in entities:
        if category and entity.category != category:
            continue
        if location and location.lower() not in str(entity.location or "").lower():
            continue
        if listing_type and entity.listing_type != listing_type:
            continue
        listings.append(_to_listing_response(entity))

    return _envelope([item.model_dump() for item in listings], meta={"total": len(listings)})


@router.get("/api/v1/market/listings/{entity_id}")
@router.get("/api/v1/listings/{entity_id}")
async def get_listing(
    entity_id: str,
    service: ListingService = Depends(get_listing_service),
):
    entity = await service.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    return _envelope(_to_listing_response(entity).model_dump())


@router.patch("/api/v1/market/listings/{entity_id}")
@router.patch("/api/v1/listings/{entity_id}")
async def update_listing(
    entity_id: str,
    body: ListingUpdate,
    request: Request,
    service: ListingService = Depends(get_listing_service),
):
    entity = await service.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    role = _user_role(request)
    user_id = _user_id(request)

    if role not in ("admin", "super_admin", "reviewer") and entity.owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to update this listing")

    patch = body.model_dump(exclude_unset=True)
    status_value = entity.status
    if "status" in patch and role in ("admin", "super_admin", "reviewer"):
        status_value = str(patch.pop("status"))

    updated = await service.update_entity(entity_id, data=patch, status=status_value)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    return _envelope(_to_listing_response(updated).model_dump())


@router.get("/api/v1/market/prices/average")
async def average_prices(
    category: Optional[str] = Query(default=None),
    service: ListingService = Depends(get_listing_service),
):
    entities = await service.list_entities(status_filter="active")
    buckets: dict[tuple[str, str], list[float]] = defaultdict(list)

    for entity in entities:
        if category and entity.category != category:
            continue
        location = str(entity.location or "unknown")
        cat = str(entity.category or "unknown")
        price = float(entity.price or 0)
        if price <= 0:
            continue
        buckets[(location, cat)].append(price)

    insights = [
        PriceInsightResponse(
            location=location,
            category=cat,
            avg_price=round(sum(values) / len(values), 2),
            listings_count=len(values),
        ).model_dump()
        for (location, cat), values in sorted(buckets.items())
    ]

    return _envelope(insights, meta={"total": len(insights)})