"""Internal routes — used by auth-service only (not exposed through gateway)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas import InternalCreateUser, InternalUserResponse
from services.user_service import (
    create_user,
    get_user_by_id,
    lookup_user,
    check_existing_user,
)

router = APIRouter(prefix="/internal/users", tags=["Internal"])


@router.post("", status_code=201)
async def internal_create_user(
    data: InternalCreateUser,
    db: AsyncSession = Depends(get_db),
):
    """Create a new user (called by auth-service during registration)."""

    # Check for duplicates
    if await check_existing_user(db, data.email, data.phone):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email or phone already exists",
        )

    user = await create_user(
        db=db,
        email=data.email,
        phone=data.phone,
        full_name=data.full_name,
        password_hash=data.password_hash,
        role=data.role,
    )

    return {
        "id": str(user.id),
        "email": user.email,
        "phone": user.phone,
        "full_name": user.full_name,
        "role": user.role,
        "status": user.status,
    }


@router.get("/lookup")
async def internal_lookup_user(
    email: str = None,
    phone: str = None,
    db: AsyncSession = Depends(get_db),
):
    """Look up a user by email or phone (called by auth-service during login)."""

    user = await lookup_user(db, email=email, phone=phone)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return InternalUserResponse(
        id=str(user.id),
        email=user.email,
        phone=user.phone,
        full_name=user.full_name,
        password_hash=user.password_hash,
        role=user.role,
        status=user.status,
    )


@router.get("/{user_id}")
async def internal_get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get user by ID (called by auth-service for token refresh)."""

    user = await get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return InternalUserResponse(
        id=str(user.id),
        email=user.email,
        phone=user.phone,
        full_name=user.full_name,
        password_hash=user.password_hash,
        role=user.role,
        status=user.status,
    )
