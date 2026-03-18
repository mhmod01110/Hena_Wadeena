"""HTTP controller for map POIs and carpool rides."""

from __future__ import annotations

from math import asin, cos, radians, sin, sqrt
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from core.dependencies import get_point_of_interest_service
from schemas.requests import POICreate, POIUpdate, CarpoolRideCreate, CarpoolRideJoin
from schemas.responses import POIResponse, CarpoolRideResponse
from services.point_of_interest_service import PointOfInterestService


router = APIRouter()


def _envelope(data: Any = None, meta: Optional[dict] = None, error: Optional[str] = None, success: bool = True) -> dict:
    return {
        "success": success,
        "data": data,
        "meta": meta,
        "error": error,
    }


def _user_id(request: Request) -> str:
    return request.headers.get("X-User-Id", "anonymous")


def _user_role(request: Request) -> str:
    return request.headers.get("X-User-Role", "tourist")


def _to_poi_response(entity) -> POIResponse:
    return POIResponse(
        id=str(entity.id),
        name_ar=entity.name_ar or "",
        name_en=entity.name_en,
        category=entity.category or "unknown",
        description=entity.description,
        address=entity.address or "",
        lat=float(entity.lat or 0.0),
        lng=float(entity.lng or 0.0),
        phone=entity.phone,
        status=entity.status,
        created_at=entity.created_at,
    )


def _to_ride_response(entity) -> CarpoolRideResponse:
    return CarpoolRideResponse(
        id=str(entity.id),
        driver_id=entity.driver_id or "anonymous",
        origin_name=entity.origin_name or "",
        destination_name=entity.destination_name or "",
        departure_time=entity.departure_time or "",
        seats_total=int(entity.seats_total or 0),
        seats_taken=int(entity.seats_taken or 0),
        price_per_seat=float(entity.price_per_seat or 0),
        notes=entity.notes,
        status=entity.status,
        created_at=entity.created_at,
    )


def _distance_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6371.0
    d_lat = radians(lat2 - lat1)
    d_lng = radians(lng2 - lng1)
    a = sin(d_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lng / 2) ** 2
    return 2 * r * asin(sqrt(a))


@router.post("/api/v1/map/pois", status_code=status.HTTP_201_CREATED)
async def create_poi(
    body: POICreate,
    request: Request,
    service: PointOfInterestService = Depends(get_point_of_interest_service),
):
    role = _user_role(request)
    poi_status = "approved" if role in ("admin", "super_admin", "reviewer") else "pending"
    payload = body.model_dump()
    payload["type"] = "poi"
    payload["created_by"] = _user_id(request)

    entity = await service.create_entity(
        title=f"poi:{body.name_ar}:{uuid4()}",
        description=body.description,
        status=poi_status,
        data=payload,
    )
    return _envelope(_to_poi_response(entity).model_dump())


@router.get("/api/v1/map/pois")
async def list_pois(
    category: Optional[str] = Query(default=None),
    q: Optional[str] = Query(default=None),
    service: PointOfInterestService = Depends(get_point_of_interest_service),
):
    entities = await service.list_entities()
    pois = []
    for entity in entities:
        if entity.entity_kind != "poi":
            continue
        if category and entity.category != category:
            continue
        if q:
            text = " ".join([
                str(entity.name_ar or ""),
                str(entity.name_en or ""),
                str(entity.description or ""),
                str(entity.address or ""),
            ]).lower()
            if q.lower() not in text:
                continue
        pois.append(_to_poi_response(entity))

    return _envelope([poi.model_dump() for poi in pois], meta={"total": len(pois)})


@router.get("/api/v1/map/pois/{entity_id}")
async def get_poi(
    entity_id: str,
    service: PointOfInterestService = Depends(get_point_of_interest_service),
):
    entity = await service.get_entity(entity_id)
    if not entity or entity.entity_kind != "poi":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POI not found")
    return _envelope(_to_poi_response(entity).model_dump())


@router.patch("/api/v1/map/pois/{entity_id}")
async def update_poi(
    entity_id: str,
    body: POIUpdate,
    request: Request,
    service: PointOfInterestService = Depends(get_point_of_interest_service),
):
    entity = await service.get_entity(entity_id)
    if not entity or entity.entity_kind != "poi":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POI not found")

    patch = body.model_dump(exclude_unset=True)
    patch["type"] = "poi"

    role = _user_role(request)
    status_value = entity.status
    if role in ("admin", "super_admin", "reviewer") and "status" in patch:
        status_value = str(patch["status"])

    updated = await service.update_entity(entity_id, data=patch, status=status_value)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POI not found")
    return _envelope(_to_poi_response(updated).model_dump())


@router.get("/api/v1/map/pois/nearby")
async def nearby_pois(
    lat: float,
    lng: float,
    radius_km: float = Query(default=10.0, gt=0, le=200),
    service: PointOfInterestService = Depends(get_point_of_interest_service),
):
    entities = await service.list_entities(status_filter="approved")
    matches = []
    for entity in entities:
        if entity.entity_kind != "poi":
            continue
        if entity.lat is None or entity.lng is None:
            continue
        distance = _distance_km(lat, lng, float(entity.lat), float(entity.lng))
        if distance <= radius_km:
            item = _to_poi_response(entity).model_dump()
            item["distance_km"] = round(distance, 2)
            matches.append(item)

    matches.sort(key=lambda item: item["distance_km"])
    return _envelope(matches, meta={"total": len(matches), "radius_km": radius_km})


@router.post("/api/v1/carpool/rides", status_code=status.HTTP_201_CREATED)
async def create_ride(
    body: CarpoolRideCreate,
    request: Request,
    service: PointOfInterestService = Depends(get_point_of_interest_service),
):
    payload = body.model_dump()
    payload.update({
        "type": "carpool_ride",
        "driver_id": _user_id(request),
        "seats_taken": 0,
    })

    entity = await service.create_entity(
        title=f"carpool:{body.origin_name}:{body.destination_name}:{uuid4()}",
        description=body.notes,
        status="open",
        data=payload,
    )
    return _envelope(_to_ride_response(entity).model_dump())


@router.get("/api/v1/carpool/rides")
async def list_rides(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    service: PointOfInterestService = Depends(get_point_of_interest_service),
):
    entities = await service.list_entities(status_filter=status_filter)
    rides = [_to_ride_response(entity).model_dump() for entity in entities if entity.entity_kind == "carpool_ride"]
    return _envelope(rides, meta={"total": len(rides)})


@router.post("/api/v1/carpool/rides/{entity_id}/join")
async def join_ride(
    entity_id: str,
    body: CarpoolRideJoin,
    service: PointOfInterestService = Depends(get_point_of_interest_service),
):
    entity = await service.get_entity(entity_id)
    if not entity or entity.entity_kind != "carpool_ride":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ride not found")

    seats_total = int(entity.seats_total or 0)
    seats_taken = int(entity.seats_taken or 0)
    remaining = seats_total - seats_taken
    if body.seats_requested > remaining:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Not enough seats available")

    patch = {
        "type": "carpool_ride",
        "seats_taken": seats_taken + body.seats_requested,
    }
    new_status = "full" if patch["seats_taken"] >= seats_total else entity.status

    updated = await service.update_entity(entity_id, data=patch, status=new_status)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ride not found")

    return _envelope(_to_ride_response(updated).model_dump())