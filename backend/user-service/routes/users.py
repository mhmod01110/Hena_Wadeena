"""User routes — public endpoints accessed through the gateway."""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas import UserProfile, UpdateProfile, UserPreferenceSchema
from services.user_service import (
    get_user_by_id,
    update_user,
    get_user_preferences,
    upsert_user_preferences,
)

router = APIRouter()


def get_current_user_id(request: Request) -> str:
    """Extract user ID from X-User-Id header (set by gateway)."""
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated",
        )
    return user_id


def get_current_user_role(request: Request) -> str:
    """Extract user role from X-User-Role header (set by gateway)."""
    return request.headers.get("X-User-Role", "tourist")


# ── GET /me ──────────────────────────────────────────────────────────────────

@router.get("/me", response_model=UserProfile)
async def get_my_profile(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Get the current user's profile."""
    user_id = get_current_user_id(request)
    user = await get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserProfile(
        id=str(user.id),
        email=user.email,
        phone=user.phone,
        full_name=user.full_name,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        role=user.role,
        status=user.status,
        language=user.language,
        verified_at=user.verified_at,
        created_at=user.created_at,
    )


# ── PUT /me ──────────────────────────────────────────────────────────────────

@router.put("/me", response_model=UserProfile)
async def update_my_profile(
    data: UpdateProfile,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Update the current user's profile."""
    user_id = get_current_user_id(request)

    update_data = data.model_dump(exclude_unset=True)
    user = await update_user(db, user_id, **update_data)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserProfile(
        id=str(user.id),
        email=user.email,
        phone=user.phone,
        full_name=user.full_name,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        role=user.role,
        status=user.status,
        language=user.language,
        verified_at=user.verified_at,
        created_at=user.created_at,
    )


# ── GET /{id} (admin only) ──────────────────────────────────────────────────

@router.get("/{user_id}", response_model=UserProfile)
async def get_user_profile(
    user_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Get any user's profile (admin only)."""
    role = get_current_user_role(request)
    if role not in ("admin", "super_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")

    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserProfile(
        id=str(user.id),
        email=user.email,
        phone=user.phone,
        full_name=user.full_name,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        role=user.role,
        status=user.status,
        language=user.language,
        verified_at=user.verified_at,
        created_at=user.created_at,
    )


# ── Preferences ──────────────────────────────────────────────────────────────

@router.get("/me/preferences", response_model=UserPreferenceSchema)
async def get_my_preferences(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Get current user's notification preferences."""
    user_id = get_current_user_id(request)
    prefs = await get_user_preferences(db, user_id)

    if not prefs:
        return UserPreferenceSchema()

    return UserPreferenceSchema(
        notify_push=prefs.notify_push,
        notify_email=prefs.notify_email,
        notify_sms=prefs.notify_sms,
        preferred_areas=prefs.preferred_areas or [],
        interests=prefs.interests or [],
    )


@router.put("/me/preferences", response_model=UserPreferenceSchema)
async def update_my_preferences(
    data: UserPreferenceSchema,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Update current user's preferences."""
    user_id = get_current_user_id(request)

    prefs = await upsert_user_preferences(
        db,
        user_id,
        notify_push=data.notify_push,
        notify_email=data.notify_email,
        notify_sms=data.notify_sms,
        preferred_areas=data.preferred_areas,
        interests=data.interests,
    )

    return UserPreferenceSchema(
        notify_push=prefs.notify_push,
        notify_email=prefs.notify_email,
        notify_sms=prefs.notify_sms,
        preferred_areas=prefs.preferred_areas or [],
        interests=prefs.interests or [],
    )
