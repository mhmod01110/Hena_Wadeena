"""HTTP controller for analytics dashboards and event ingestion."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from core.dependencies import get_metric_event_service
from schemas.requests import EventIngestRequest, ExportRequest
from schemas.responses import EventIngestResponse
from services.metric_event_service import MetricEventService


router = APIRouter()

_ADMIN_ROLES = {"admin", "super_admin"}


def _envelope(data: Any = None, meta: Optional[dict] = None, error: Optional[str] = None, success: bool = True) -> dict:
    return {"success": success, "data": data, "meta": meta, "error": error}


def _current_user(request: Request) -> tuple[str, str]:
    user_id = request.headers.get("X-User-Id")
    role = request.headers.get("X-User-Role", "tourist")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")
    return user_id, role


def _require_admin(role: str) -> None:
    if role not in _ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")


def _date_range(date_from: Optional[date], date_to: Optional[date]) -> tuple[date, date]:
    resolved_to = date_to or date.today()
    resolved_from = date_from or (resolved_to - timedelta(days=30))
    if resolved_from > resolved_to:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="date_from must be <= date_to")
    return resolved_from, resolved_to


@router.post("/api/v1/analytics/events", status_code=status.HTTP_201_CREATED)
async def ingest_event(
    body: EventIngestRequest,
    request: Request,
    service: MetricEventService = Depends(get_metric_event_service),
):
    user_id, role = _current_user(request)
    _require_admin(role)

    event = await service.ingest_event(
        event_type=body.event_type,
        actor_id=body.actor_id or user_id,
        actor_role=body.actor_role,
        entity_type=body.entity_type,
        entity_id=body.entity_id,
        amount=body.amount,
        city=body.city,
        payment_method=body.payment_method,
        price=body.price,
        query=body.query,
        results_count=body.results_count,
        occurred_at=body.occurred_at,
    )

    payload = EventIngestResponse(
        id=str(event.id),
        event_type=event.event_type,
        actor_id=event.actor_id,
        actor_role=event.actor_role,
        entity_type=event.entity_type,
        entity_id=event.entity_id,
        amount=event.amount,
        city=event.city,
        payment_method=event.payment_method,
        price=event.list_price,
        query=event.search_query,
        results_count=event.results_count,
        created_at=event.created_at,
    )
    return _envelope(payload.model_dump())


@router.get("/api/v1/analytics/overview")
async def overview(
    request: Request,
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    service: MetricEventService = Depends(get_metric_event_service),
):
    _, role = _current_user(request)
    _require_admin(role)

    resolved_from, resolved_to = _date_range(date_from, date_to)
    payload = await service.platform_overview(resolved_from, resolved_to)
    return _envelope(payload)


@router.get("/api/v1/analytics/users")
async def user_analytics(
    request: Request,
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    role_filter: Optional[str] = Query(default=None, alias="role"),
    service: MetricEventService = Depends(get_metric_event_service),
):
    _, role = _current_user(request)
    _require_admin(role)

    resolved_from, resolved_to = _date_range(date_from, date_to)
    payload = await service.user_analytics(resolved_from, resolved_to, role_filter)
    return _envelope(payload)


@router.get("/api/v1/analytics/listings")
async def listing_analytics(
    request: Request,
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    city: Optional[str] = Query(default=None),
    service: MetricEventService = Depends(get_metric_event_service),
):
    _, role = _current_user(request)
    _require_admin(role)

    resolved_from, resolved_to = _date_range(date_from, date_to)
    payload = await service.listing_analytics(resolved_from, resolved_to, city)
    return _envelope(payload)


@router.get("/api/v1/analytics/bookings")
async def booking_analytics(
    request: Request,
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    service: MetricEventService = Depends(get_metric_event_service),
):
    _, role = _current_user(request)
    _require_admin(role)

    resolved_from, resolved_to = _date_range(date_from, date_to)
    payload = await service.booking_analytics(resolved_from, resolved_to)
    return _envelope(payload)


@router.get("/api/v1/analytics/revenue")
async def revenue_analytics(
    request: Request,
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    method: Optional[str] = Query(default=None),
    service: MetricEventService = Depends(get_metric_event_service),
):
    _, role = _current_user(request)
    _require_admin(role)

    resolved_from, resolved_to = _date_range(date_from, date_to)
    payload = await service.revenue_analytics(resolved_from, resolved_to, method)
    return _envelope(payload)


@router.get("/api/v1/analytics/search")
async def search_analytics(
    request: Request,
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    top_n: int = Query(default=20, ge=1, le=100),
    service: MetricEventService = Depends(get_metric_event_service),
):
    _, role = _current_user(request)
    _require_admin(role)

    resolved_from, resolved_to = _date_range(date_from, date_to)
    payload = await service.search_analytics(resolved_from, resolved_to, top_n)
    return _envelope(payload)


@router.get("/api/v1/analytics/market/heatmap")
async def market_heatmap(
    request: Request,
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    service: MetricEventService = Depends(get_metric_event_service),
):
    _, role = _current_user(request)
    _require_admin(role)

    resolved_from, resolved_to = _date_range(date_from, date_to)
    payload = await service.market_heatmap(resolved_from, resolved_to)
    return _envelope(payload)


@router.get("/api/v1/analytics/kpis")
async def kpis(
    request: Request,
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    service: MetricEventService = Depends(get_metric_event_service),
):
    _, role = _current_user(request)
    _require_admin(role)

    resolved_from, resolved_to = _date_range(date_from, date_to)
    payload = await service.kpis(resolved_from, resolved_to)
    return _envelope(payload)


@router.post("/api/v1/analytics/export", status_code=status.HTTP_202_ACCEPTED)
async def export_analytics(
    body: ExportRequest,
    request: Request,
    service: MetricEventService = Depends(get_metric_event_service),
):
    _, role = _current_user(request)
    _require_admin(role)

    if body.date_from > body.date_to:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="date_from must be <= date_to")

    payload = await service.export_report(
        report_type=body.report_type,
        date_from=body.date_from,
        date_to=body.date_to,
        fmt=body.format,
    )
    return _envelope(payload)
