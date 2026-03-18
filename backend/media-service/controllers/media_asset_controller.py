"""HTTP controller for media asset lifecycle."""

from __future__ import annotations

from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status

from core.dependencies import get_media_asset_service
from schemas.requests import MediaAssetComplete, MediaAssetCreate
from schemas.responses import MediaAssetResponse
from services.media_asset_service import MediaAssetService


router = APIRouter()


_ADMIN_ROLES = {"admin", "super_admin"}


def _envelope(data: Any = None, meta: Optional[dict] = None, error: Optional[str] = None, success: bool = True) -> dict:
    return {"success": success, "data": data, "meta": meta, "error": error}


def _uid(request: Request) -> str:
    uid = request.headers.get("X-User-Id")
    if not uid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")
    return uid


def _role(request: Request) -> str:
    return request.headers.get("X-User-Role", "tourist")


def _to_asset(entity) -> MediaAssetResponse:
    return MediaAssetResponse(
        id=str(entity.id),
        owner_id=entity.owner_id,
        file_name=entity.file_name,
        mime_type=entity.mime_type,
        size_bytes=int(entity.size_bytes),
        checksum=entity.checksum,
        url=entity.url,
        status=entity.status,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def _can_manage_asset(role: str, owner_id: str, user_id: str) -> bool:
    return role in _ADMIN_ROLES or owner_id == user_id


@router.post("/api/v1/media/assets", status_code=status.HTTP_201_CREATED)
@router.post("/api/v1/media/upload/initiate", status_code=status.HTTP_201_CREATED)
async def create_asset(
    body: MediaAssetCreate,
    request: Request,
    service: MediaAssetService = Depends(get_media_asset_service),
):
    uid = _uid(request)

    entity = await service.create_entity(
        title=f"media:{uid}:{body.file_name}:{uuid4()}",
        owner_id=uid,
        file_name=body.file_name,
        mime_type=body.mime_type,
        size_bytes=body.size_bytes,
        checksum=body.checksum,
        status="pending",
        url=None,
    )
    return _envelope(_to_asset(entity).model_dump())


@router.get("/api/v1/media/assets")
async def list_assets(
    request: Request,
    mine_only: bool = Query(default=True),
    service: MediaAssetService = Depends(get_media_asset_service),
):
    uid = _uid(request)
    role = _role(request)

    entities = await service.list_entities()
    items = []
    for entity in entities:
        if entity.status == "deleted":
            continue
        if mine_only and not _can_manage_asset(role, entity.owner_id, uid):
            continue
        items.append(_to_asset(entity))

    items.sort(key=lambda item: item.created_at, reverse=True)
    return _envelope([item.model_dump() for item in items], meta={"total": len(items)})


@router.get("/api/v1/media/assets/{entity_id}")
async def get_asset(
    entity_id: str,
    request: Request,
    service: MediaAssetService = Depends(get_media_asset_service),
):
    uid = _uid(request)
    role = _role(request)

    entity = await service.get_entity(entity_id)
    if not entity or entity.status == "deleted":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    if not _can_manage_asset(role, entity.owner_id, uid):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    return _envelope(_to_asset(entity).model_dump())


@router.patch("/api/v1/media/assets/{entity_id}/complete")
@router.post("/api/v1/media/upload/complete/{entity_id}")
async def complete_asset(
    entity_id: str,
    body: MediaAssetComplete,
    request: Request,
    service: MediaAssetService = Depends(get_media_asset_service),
):
    uid = _uid(request)
    role = _role(request)

    entity = await service.get_entity(entity_id)
    if not entity or entity.status == "deleted":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    if not _can_manage_asset(role, entity.owner_id, uid):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    updated = await service.update_entity(entity_id, url=body.url, status=body.status)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    return _envelope(_to_asset(updated).model_dump())


@router.delete("/api/v1/media/assets/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    entity_id: str,
    request: Request,
    service: MediaAssetService = Depends(get_media_asset_service),
):
    uid = _uid(request)
    role = _role(request)

    entity = await service.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    if not _can_manage_asset(role, entity.owner_id, uid):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    await service.update_entity(entity_id, status="deleted")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
