"""
Internal controller for service-to-service endpoints.
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
            email=body.email,
            phone=body.phone,
            full_name=body.full_name,
            password_hash=body.password_hash,
            role=body.role,
            city=body.city,
            organization=body.organization,
            documents=[document.model_dump() for document in body.documents],
        )
    except ValueError as exc:
        raise HTTPException(409, str(exc))
    except Exception as exc:
        raise HTTPException(500, f"Failed to create user: {exc}")

    return {
        "id": str(user.id),
        "email": user.email,
        "phone": user.phone,
        "full_name": user.full_name,
        "display_name": user.display_name,
        "avatar_url": user.avatar_url,
        "city": user.city,
        "organization": user.organization,
        "language": user.language,
        "role": user.role,
        "status": user.status,
    }


@router.get("/lookup", response_model=InternalUserResponse)
async def lookup_user(
    email: str = None,
    phone: str = None,
    svc: UserService = Depends(get_user_service),
):
    user = await svc.lookup_user(email=email, phone=phone)
    if not user:
        raise HTTPException(404, "User not found")

    return InternalUserResponse(
        id=str(user.id),
        email=user.email,
        phone=user.phone,
        full_name=user.full_name,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        city=user.city,
        organization=user.organization,
        language=user.language,
        password_hash=user.password_hash,
        role=user.role,
        status=user.status,
    )


@router.get("/{user_id}", response_model=InternalUserResponse)
async def get_user(
    user_id: str,
    svc: UserService = Depends(get_user_service),
):
    user = await svc.get_user(user_id)
    if not user:
        raise HTTPException(404, "User not found")

    return InternalUserResponse(
        id=str(user.id),
        email=user.email,
        phone=user.phone,
        full_name=user.full_name,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        city=user.city,
        organization=user.organization,
        language=user.language,
        password_hash=user.password_hash,
        role=user.role,
        status=user.status,
    )
