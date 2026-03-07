"""
Internal controller — service-to-service endpoints (auth-service → user-service).
Not exposed through the API gateway.
"""

from fastapi import APIRouter, Depends, HTTPException

from schemas.requests import InternalCreateUser
from schemas.responses import InternalUserResponse
from services.user_service import UserService
from core.dependencies import get_user_service

router = APIRouter(prefix="/internal/users", tags=["Internal"])


@router.post("", status_code=201)
async def create_user(
    body: InternalCreateUser,
    svc: UserService = Depends(get_user_service),
):
    try:
        user = await svc.create_user(
            email=body.email, phone=body.phone,
            full_name=body.full_name, password_hash=body.password_hash,
            role=body.role,
        )
    except ValueError as e:
        raise HTTPException(409, str(e))

    return {
        "id": str(user.id), "email": user.email, "phone": user.phone,
        "full_name": user.full_name, "role": user.role, "status": user.status,
    }


@router.get("/lookup")
async def lookup_user(
    email: str = None,
    phone: str = None,
    svc: UserService = Depends(get_user_service),
):
    user = await svc.lookup_user(email=email, phone=phone)
    if not user:
        raise HTTPException(404, "User not found")
    return InternalUserResponse(
        id=str(user.id), email=user.email, phone=user.phone,
        full_name=user.full_name, password_hash=user.password_hash,
        role=user.role, status=user.status,
    )


@router.get("/{user_id}")
async def get_user(
    user_id: str,
    svc: UserService = Depends(get_user_service),
):
    user = await svc.get_user(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return InternalUserResponse(
        id=str(user.id), email=user.email, phone=user.phone,
        full_name=user.full_name, password_hash=user.password_hash,
        role=user.role, status=user.status,
    )
