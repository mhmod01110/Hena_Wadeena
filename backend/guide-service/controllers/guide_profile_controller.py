"""HTTP controller for guides and bookings."""

from __future__ import annotations

from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from core.dependencies import get_guide_profile_service
from schemas.requests import GuideProfileCreate, GuideProfileUpdate, BookingCreate, BookingStatusUpdate
from schemas.responses import GuideProfileResponse, BookingResponse
from services.guide_profile_service import GuideProfileService


router = APIRouter()


GUIDE_ROLES = {"guide", "admin", "super_admin"}
REVIEW_ROLES = {"reviewer", "admin", "super_admin"}


def _envelope(data: Any = None, meta: Optional[dict] = None, error: Optional[str] = None, success: bool = True) -> dict:
    return {"success": success, "data": data, "meta": meta, "error": error}


def _user_id(request: Request) -> str:
    uid = request.headers.get("X-User-Id")
    if not uid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")
    return uid


def _user_role(request: Request) -> str:
    return request.headers.get("X-User-Role", "tourist")


def _parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _to_profile(entity) -> GuideProfileResponse:
    return GuideProfileResponse(
        id=str(entity.id),
        user_id=entity.user_id or "unknown",
        display_name=entity.display_name or "",
        bio=entity.bio or "",
        languages=_parse_csv(entity.languages_csv),
        specialties=_parse_csv(entity.specialties_csv),
        base_price=float(entity.base_price or 0),
        active=bool(entity.active),
        verified=bool(entity.verified),
        created_at=entity.created_at,
    )


def _to_booking(entity) -> BookingResponse:
    return BookingResponse(
        id=str(entity.id),
        guide_profile_id=entity.guide_profile_id or "",
        guide_user_id=entity.guide_user_id or "",
        tourist_id=entity.tourist_id or "",
        booking_date=entity.booking_date or "",
        start_time=entity.start_time or "",
        people_count=int(entity.people_count or 1),
        total_price=float(entity.total_price or 0),
        notes=entity.notes,
        status=entity.status,
        created_at=entity.created_at,
    )


@router.post("/api/v1/guides/profiles", status_code=status.HTTP_201_CREATED)
async def create_profile(
    body: GuideProfileCreate,
    request: Request,
    service: GuideProfileService = Depends(get_guide_profile_service),
):
    role = _user_role(request)
    if role not in GUIDE_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only guides can create guide profiles")

    user_id = _user_id(request)
    payload = body.model_dump()
    payload.update({
        "type": "guide_profile",
        "user_id": user_id,
        "active": True,
        "verified": role in REVIEW_ROLES,
    })

    entity = await service.create_entity(
        title=f"guide-profile:{user_id}:{uuid4()}",
        description=body.bio,
        status="active",
        data=payload,
    )
    return _envelope(_to_profile(entity).model_dump())


@router.get("/api/v1/guides/profiles")
async def list_profiles(
    specialty: Optional[str] = Query(default=None),
    active: Optional[bool] = Query(default=True),
    service: GuideProfileService = Depends(get_guide_profile_service),
):
    entities = await service.list_entities(status_filter="active" if active else None)
    items = []
    for entity in entities:
        if entity.entity_kind != "guide_profile":
            continue
        if active is not None and bool(entity.active) != active:
            continue
        specialties = _parse_csv(entity.specialties_csv)
        if specialty and specialty not in specialties:
            continue
        items.append(_to_profile(entity))
    return _envelope([item.model_dump() for item in items], meta={"total": len(items)})


@router.get("/api/v1/guides/profiles/{entity_id}")
async def get_profile(
    entity_id: str,
    service: GuideProfileService = Depends(get_guide_profile_service),
):
    entity = await service.get_entity(entity_id)
    if not entity or entity.entity_kind != "guide_profile":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guide profile not found")
    return _envelope(_to_profile(entity).model_dump())


@router.patch("/api/v1/guides/profiles/{entity_id}")
async def update_profile(
    entity_id: str,
    body: GuideProfileUpdate,
    request: Request,
    service: GuideProfileService = Depends(get_guide_profile_service),
):
    entity = await service.get_entity(entity_id)
    if not entity or entity.entity_kind != "guide_profile":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guide profile not found")

    role = _user_role(request)
    user_id = _user_id(request)
    if role not in REVIEW_ROLES and entity.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to update this profile")

    patch = body.model_dump(exclude_unset=True)
    patch["type"] = "guide_profile"
    updated = await service.update_entity(entity_id, data=patch)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guide profile not found")

    return _envelope(_to_profile(updated).model_dump())


@router.post("/api/v1/bookings", status_code=status.HTTP_201_CREATED)
async def create_booking(
    body: BookingCreate,
    request: Request,
    service: GuideProfileService = Depends(get_guide_profile_service),
):
    tourist_id = _user_id(request)

    guide_entity = await service.get_entity(body.guide_profile_id)
    if not guide_entity or guide_entity.entity_kind != "guide_profile":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guide profile not found")

    total_price = float(guide_entity.base_price or 0) * body.people_count
    payload = body.model_dump()
    payload.update({
        "type": "booking",
        "tourist_id": tourist_id,
        "guide_user_id": guide_entity.user_id,
        "total_price": total_price,
    })

    entity = await service.create_entity(
        title=f"booking:{body.guide_profile_id}:{tourist_id}:{uuid4()}",
        description=body.notes,
        status="pending",
        data=payload,
    )
    return _envelope(_to_booking(entity).model_dump())


@router.get("/api/v1/bookings")
async def list_bookings(
    request: Request,
    mine_only: bool = Query(default=True),
    service: GuideProfileService = Depends(get_guide_profile_service),
):
    uid = _user_id(request)
    role = _user_role(request)

    entities = await service.list_entities()
    items = []
    for entity in entities:
        if entity.entity_kind != "booking":
            continue

        if mine_only and role not in REVIEW_ROLES:
            if entity.tourist_id != uid and entity.guide_user_id != uid:
                continue

        items.append(_to_booking(entity))

    return _envelope([item.model_dump() for item in items], meta={"total": len(items)})


@router.patch("/api/v1/bookings/{entity_id}/status")
async def update_booking_status(
    entity_id: str,
    body: BookingStatusUpdate,
    request: Request,
    service: GuideProfileService = Depends(get_guide_profile_service),
):
    uid = _user_id(request)
    role = _user_role(request)

    entity = await service.get_entity(entity_id)
    if not entity or entity.entity_kind != "booking":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    if role not in REVIEW_ROLES and entity.guide_user_id != uid and entity.tourist_id != uid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to update this booking")

    updated = await service.update_entity(entity_id, status=body.status)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    return _envelope(_to_booking(updated).model_dump())