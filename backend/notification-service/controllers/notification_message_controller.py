"""HTTP controller for notifications."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status

from core.dependencies import get_notification_message_service
from schemas.requests import NotificationCreate, PreferenceUpdate, MarkReadRequest
from schemas.responses import NotificationResponse, PreferenceResponse
from services.notification_message_service import NotificationMessageService


router = APIRouter()


ADMIN_ROLES = {"admin", "super_admin", "reviewer"}


def _envelope(data: Any = None, meta: Optional[dict] = None, error: Optional[str] = None, success: bool = True) -> dict:
    return {"success": success, "data": data, "meta": meta, "error": error}


def _uid(request: Request) -> str:
    uid = request.headers.get("X-User-Id")
    if not uid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")
    return uid


def _role(request: Request) -> str:
    return request.headers.get("X-User-Role", "tourist")


def _parse_channel_csv(value: str | None) -> list[str]:
    if not value:
        return ["in_app"]
    return [item.strip() for item in value.split(",") if item.strip()]


def _to_notification(entity) -> NotificationResponse:
    return NotificationResponse(
        id=str(entity.id),
        user_id=entity.user_id,
        type=entity.notif_type or "system",
        title=entity.notif_title or "",
        body=entity.notif_body or "",
        channel=_parse_channel_csv(entity.channel_csv),
        read_at=entity.read_at,
        status=entity.status,
        created_at=entity.created_at,
    )


async def _create_pref_if_missing(service: NotificationMessageService, user_id: str):
    entities = await service.list_entities()
    for entity in entities:
        if entity.entity_kind == "preference" and entity.user_id == user_id:
            return entity

    payload = {
        "type": "preference",
        "user_id": user_id,
        "notify_push": True,
        "notify_email": True,
        "notify_sms": False,
    }
    return await service.create_entity(
        title=f"pref:{user_id}:{uuid4()}",
        description="notification preferences",
        status="active",
        data=payload,
    )


@router.get("/api/v1/notifications")
async def list_my_notifications(
    request: Request,
    service: NotificationMessageService = Depends(get_notification_message_service),
):
    uid = _uid(request)
    entities = await service.list_entities()
    result = []
    for entity in entities:
        if entity.entity_kind == "preference":
            continue
        if entity.user_id != uid:
            continue
        result.append(_to_notification(entity))

    result.sort(key=lambda item: item.created_at, reverse=True)
    return _envelope([item.model_dump() for item in result], meta={"total": len(result)})


@router.get("/api/v1/notifications/unread-count")
async def unread_count(
    request: Request,
    service: NotificationMessageService = Depends(get_notification_message_service),
):
    uid = _uid(request)
    entities = await service.list_entities()
    count = 0
    for entity in entities:
        if entity.entity_kind == "preference":
            continue
        if entity.user_id != uid:
            continue
        if not entity.read_at:
            count += 1
    return _envelope({"count": count})


@router.patch("/api/v1/notifications/{entity_id}/read")
async def mark_read(
    entity_id: str,
    body: MarkReadRequest,
    request: Request,
    service: NotificationMessageService = Depends(get_notification_message_service),
):
    uid = _uid(request)
    entity = await service.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    if entity.user_id != uid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    payload = {
        "type": entity.notif_type,
        "read_at": datetime.now(timezone.utc).isoformat() if body.read else None,
    }
    updated = await service.update_entity(entity_id, data=payload)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    return _envelope(_to_notification(updated).model_dump())


@router.get("/api/v1/notifications/preferences")
async def get_preferences(
    request: Request,
    service: NotificationMessageService = Depends(get_notification_message_service),
):
    uid = _uid(request)
    entity = await _create_pref_if_missing(service, uid)
    return _envelope(PreferenceResponse(
        user_id=uid,
        notify_push=bool(entity.notify_push),
        notify_email=bool(entity.notify_email),
        notify_sms=bool(entity.notify_sms),
    ).model_dump())


@router.put("/api/v1/notifications/preferences")
async def update_preferences(
    body: PreferenceUpdate,
    request: Request,
    service: NotificationMessageService = Depends(get_notification_message_service),
):
    uid = _uid(request)
    entity = await _create_pref_if_missing(service, uid)

    patch = body.model_dump()
    patch["type"] = "preference"

    updated = await service.update_entity(entity.id, data=patch)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preference not found")

    return _envelope(PreferenceResponse(
        user_id=uid,
        notify_push=bool(updated.notify_push),
        notify_email=bool(updated.notify_email),
        notify_sms=bool(updated.notify_sms),
    ).model_dump())


@router.post("/api/v1/notifications/send", status_code=status.HTTP_201_CREATED)
async def send_notification(
    body: NotificationCreate,
    request: Request,
    service: NotificationMessageService = Depends(get_notification_message_service),
):
    if _role(request) not in ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")

    payload = body.model_dump()
    payload["read_at"] = None

    entity = await service.create_entity(
        title=f"notification:{body.user_id}:{uuid4()}",
        description=body.body,
        status="sent",
        data=payload,
    )

    return _envelope(_to_notification(entity).model_dump())