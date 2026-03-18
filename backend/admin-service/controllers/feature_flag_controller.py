"""HTTP controller for admin and moderation workflows."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status

from core.dependencies import get_admin_service
from schemas.requests import (
    AnnouncementCreateRequest,
    AnnouncementUpdateRequest,
    FeatureFlagUpdateRequest,
    ModerationReviewRequest,
    ReportContentRequest,
    SuspendUserRequest,
)
from schemas.responses import (
    AdminUserResponse,
    AnnouncementResponse,
    AuditLogResponse,
    FeatureFlagResponse,
    ModerationQueueResponse,
)
from services.admin_service import AdminService


router = APIRouter()

_ADMIN_ROLES = {"admin", "super_admin"}
_MODERATOR_ROLES = {"reviewer", "admin", "super_admin"}
_SUPER_ADMIN_ROLES = {"super_admin"}


def _envelope(data: Any = None, meta: Optional[dict] = None, error: Optional[str] = None, success: bool = True) -> dict:
    return {"success": success, "data": data, "meta": meta, "error": error}


def _current_user(request: Request, require_auth: bool = True) -> tuple[str, str]:
    user_id = request.headers.get("X-User-Id")
    role = request.headers.get("X-User-Role", "tourist")
    if require_auth and not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")
    return user_id or "anonymous", role


def _require_role(role: str, allowed: set[str]) -> None:
    if role not in allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")


def _to_moderation(item) -> ModerationQueueResponse:
    return ModerationQueueResponse(
        id=str(item.id),
        resource_type=item.resource_type,
        resource_id=item.resource_id,
        submitted_by=item.submitted_by,
        reason=item.reason,
        status=item.status,
        reviewer_id=item.reviewer_id,
        review_note=item.review_note,
        reviewed_at=item.reviewed_at,
        subject_title=item.subject_title,
        subject_category=item.subject_category,
        source_service=item.source_service,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _to_user(user) -> AdminUserResponse:
    return AdminUserResponse(
        id=str(user.id),
        display_name=user.display_name,
        email=user.email,
        role=user.role,
        is_suspended=bool(user.is_suspended),
        is_verified=bool(user.is_verified),
        suspended_reason=user.suspended_reason,
        suspended_by=user.suspended_by,
        suspended_at=user.suspended_at,
        unsuspended_by=user.unsuspended_by,
        unsuspended_at=user.unsuspended_at,
        verified_by=user.verified_by,
        verified_at=user.verified_at,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def _to_flag(flag) -> FeatureFlagResponse:
    return FeatureFlagResponse(
        key=flag.key,
        enabled=flag.status == "active",
        description=flag.description,
        rollout_percentage=int(flag.rollout_percentage or 0),
        owner_group=flag.owner_group,
        updated_at=flag.updated_at,
    )


def _to_audit(log) -> AuditLogResponse:
    return AuditLogResponse(
        id=str(log.id),
        action=log.action,
        actor_id=log.actor_id,
        target_type=log.target_type,
        target_id=log.target_id,
        detail_status=log.detail_status,
        detail_reason=log.detail_reason,
        detail_note=log.detail_note,
        detail_queue_id=log.detail_queue_id,
        created_at=log.created_at,
    )


def _to_announcement(item) -> AnnouncementResponse:
    return AnnouncementResponse(
        id=str(item.id),
        title=item.title,
        body=item.body,
        audience=item.audience,
        status=item.status,
        priority=item.priority,
        created_by=item.created_by,
        starts_at=item.starts_at,
        ends_at=item.ends_at,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.get("/api/v1/admin/moderation")
async def list_moderation(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status_filter: Optional[str] = Query(default=None, alias="status"),
    resource_type: Optional[str] = Query(default=None),
    service: AdminService = Depends(get_admin_service),
):
    user_id, role = _current_user(request)
    _require_role(role, _MODERATOR_ROLES)
    await service.ensure_actor(user_id, role)

    items, total = await service.list_moderation_items(
        page=page,
        page_size=page_size,
        status_filter=status_filter,
        resource_type=resource_type,
    )
    payload = [_to_moderation(item).model_dump() for item in items]
    meta = {"page": page, "page_size": page_size, "total": total}
    return _envelope(payload, meta=meta)


@router.get("/api/v1/admin/moderation/{queue_id}")
async def get_moderation_item(
    queue_id: str,
    request: Request,
    service: AdminService = Depends(get_admin_service),
):
    user_id, role = _current_user(request)
    _require_role(role, _MODERATOR_ROLES)
    await service.ensure_actor(user_id, role)

    item = await service.get_moderation_item(queue_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Moderation item not found")

    return _envelope(_to_moderation(item).model_dump())


@router.patch("/api/v1/admin/moderation/{queue_id}")
async def review_moderation_item(
    queue_id: str,
    body: ModerationReviewRequest,
    request: Request,
    service: AdminService = Depends(get_admin_service),
):
    user_id, role = _current_user(request)
    _require_role(role, _MODERATOR_ROLES)
    await service.ensure_actor(user_id, role)

    item = await service.review_moderation_item(
        queue_id=queue_id,
        reviewer_id=user_id,
        status=body.status,
        note=body.note,
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Moderation item not found")

    return _envelope(_to_moderation(item).model_dump())


@router.get("/api/v1/admin/users")
async def list_users(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    role_filter: Optional[str] = Query(default=None, alias="role"),
    search: Optional[str] = Query(default=None),
    service: AdminService = Depends(get_admin_service),
):
    user_id, role = _current_user(request)
    _require_role(role, _ADMIN_ROLES)
    await service.ensure_actor(user_id, role)

    users, total = await service.list_users(page=page, page_size=page_size, role=role_filter, search=search)
    payload = [_to_user(user).model_dump() for user in users]
    meta = {"page": page, "page_size": page_size, "total": total}
    return _envelope(payload, meta=meta)


@router.get("/api/v1/admin/users/{user_id}")
async def get_user(
    user_id: str,
    request: Request,
    service: AdminService = Depends(get_admin_service),
):
    actor_id, actor_role = _current_user(request)
    _require_role(actor_role, _ADMIN_ROLES)
    await service.ensure_actor(actor_id, actor_role)

    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return _envelope(_to_user(user).model_dump())


@router.patch("/api/v1/admin/users/{user_id}/suspend")
async def suspend_user(
    user_id: str,
    body: SuspendUserRequest,
    request: Request,
    service: AdminService = Depends(get_admin_service),
):
    actor_id, actor_role = _current_user(request)
    _require_role(actor_role, _ADMIN_ROLES)
    await service.ensure_actor(actor_id, actor_role)

    user = await service.suspend_user(user_id=user_id, actor_id=actor_id, reason=body.reason)
    return _envelope(_to_user(user).model_dump())


@router.patch("/api/v1/admin/users/{user_id}/unsuspend")
async def unsuspend_user(
    user_id: str,
    request: Request,
    service: AdminService = Depends(get_admin_service),
):
    actor_id, actor_role = _current_user(request)
    _require_role(actor_role, _SUPER_ADMIN_ROLES)
    await service.ensure_actor(actor_id, actor_role)

    user = await service.unsuspend_user(user_id=user_id, actor_id=actor_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return _envelope(_to_user(user).model_dump())


@router.patch("/api/v1/admin/users/{user_id}/verify")
async def verify_user(
    user_id: str,
    request: Request,
    service: AdminService = Depends(get_admin_service),
):
    actor_id, actor_role = _current_user(request)
    _require_role(actor_role, _ADMIN_ROLES)
    await service.ensure_actor(actor_id, actor_role)

    user = await service.verify_user(user_id=user_id, actor_id=actor_id)
    return _envelope(_to_user(user).model_dump())


@router.get("/api/v1/admin/flags")
async def list_flags(request: Request, service: AdminService = Depends(get_admin_service)):
    actor_id, actor_role = _current_user(request)
    _require_role(actor_role, _SUPER_ADMIN_ROLES)
    await service.ensure_actor(actor_id, actor_role)

    flags = await service.list_flags()
    return _envelope([_to_flag(flag).model_dump() for flag in flags], meta={"total": len(flags)})


@router.patch("/api/v1/admin/flags/{flag_key}")
async def update_flag(
    flag_key: str,
    body: FeatureFlagUpdateRequest,
    request: Request,
    service: AdminService = Depends(get_admin_service),
):
    actor_id, actor_role = _current_user(request)
    _require_role(actor_role, _SUPER_ADMIN_ROLES)
    await service.ensure_actor(actor_id, actor_role)

    flag = await service.upsert_flag(
        flag_key=flag_key,
        enabled=body.enabled,
        actor_id=actor_id,
        description=body.description,
        rollout_percentage=body.rollout_percentage,
        owner_group=body.owner_group,
    )
    return _envelope(_to_flag(flag).model_dump())


@router.get("/api/v1/admin/audit-log")
async def list_audit_log(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=30, ge=1, le=100),
    action: Optional[str] = Query(default=None),
    service: AdminService = Depends(get_admin_service),
):
    actor_id, actor_role = _current_user(request)
    _require_role(actor_role, _SUPER_ADMIN_ROLES)
    await service.ensure_actor(actor_id, actor_role)

    logs, total = await service.list_audit_logs(page=page, page_size=page_size, action=action)
    payload = [_to_audit(log).model_dump() for log in logs]
    return _envelope(payload, meta={"page": page, "page_size": page_size, "total": total})


@router.get("/api/v1/admin/announcements")
async def list_announcements(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: AdminService = Depends(get_admin_service),
):
    actor_id, actor_role = _current_user(request)
    _require_role(actor_role, _ADMIN_ROLES)
    await service.ensure_actor(actor_id, actor_role)

    items, total = await service.list_announcements(page=page, page_size=page_size, active_only=False)
    payload = [_to_announcement(item).model_dump() for item in items]
    return _envelope(payload, meta={"page": page, "page_size": page_size, "total": total})


@router.get("/api/v1/admin/announcements/active")
async def active_announcements(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: AdminService = Depends(get_admin_service),
):
    items, total = await service.list_announcements(page=page, page_size=page_size, active_only=True)
    payload = [_to_announcement(item).model_dump() for item in items]
    return _envelope(payload, meta={"page": page, "page_size": page_size, "total": total})


@router.post("/api/v1/admin/announcements", status_code=status.HTTP_201_CREATED)
async def create_announcement(
    body: AnnouncementCreateRequest,
    request: Request,
    service: AdminService = Depends(get_admin_service),
):
    actor_id, actor_role = _current_user(request)
    _require_role(actor_role, _ADMIN_ROLES)
    await service.ensure_actor(actor_id, actor_role)

    item = await service.create_announcement(
        title=body.title,
        body=body.body,
        audience=body.audience,
        status=body.status,
        priority=body.priority,
        created_by=actor_id,
        starts_at=body.starts_at,
        ends_at=body.ends_at,
    )
    return _envelope(_to_announcement(item).model_dump())


@router.patch("/api/v1/admin/announcements/{announcement_id}")
async def update_announcement(
    announcement_id: str,
    body: AnnouncementUpdateRequest,
    request: Request,
    service: AdminService = Depends(get_admin_service),
):
    actor_id, actor_role = _current_user(request)
    _require_role(actor_role, _ADMIN_ROLES)
    await service.ensure_actor(actor_id, actor_role)

    item = await service.update_announcement(
        announcement_id=announcement_id,
        actor_id=actor_id,
        title=body.title,
        body=body.body,
        audience=body.audience,
        status=body.status,
        priority=body.priority,
        starts_at=body.starts_at,
        ends_at=body.ends_at,
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Announcement not found")

    return _envelope(_to_announcement(item).model_dump())


@router.delete("/api/v1/admin/announcements/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_announcement(
    announcement_id: str,
    request: Request,
    service: AdminService = Depends(get_admin_service),
):
    actor_id, actor_role = _current_user(request)
    _require_role(actor_role, _ADMIN_ROLES)
    await service.ensure_actor(actor_id, actor_role)

    deleted = await service.delete_announcement(announcement_id=announcement_id, actor_id=actor_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Announcement not found")

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/api/v1/admin/report", status_code=status.HTTP_202_ACCEPTED)
async def report_content(
    body: ReportContentRequest,
    request: Request,
    service: AdminService = Depends(get_admin_service),
):
    user_id, role = _current_user(request)
    await service.ensure_actor(user_id, role)

    item = await service.submit_report(
        reporter_id=user_id,
        resource_type=body.resource_type,
        resource_id=body.resource_id,
        reason=body.reason,
        subject_title=body.subject_title,
        subject_category=body.subject_category,
        source_service=body.source_service,
    )
    return _envelope(_to_moderation(item).model_dump())
