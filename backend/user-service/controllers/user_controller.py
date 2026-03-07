"""
User controller — thin HTTP layer for public and KYC endpoints.
All BL delegated to UserService.
"""

from fastapi import APIRouter, Depends, HTTPException, Request

from schemas.requests import UpdateProfile, UpdatePreferences, KYCUpload
from schemas.responses import UserProfile, PreferenceResponse, KYCStatusResponse
from services.user_service import UserService
from core.dependencies import get_user_service

router = APIRouter()


def _user_id(request: Request) -> str:
    uid = request.headers.get("X-User-Id")
    if not uid:
        raise HTTPException(401, "User not authenticated")
    return uid


def _user_role(request: Request) -> str:
    return request.headers.get("X-User-Role", "tourist")


# ── Profile ──────────────────────────────────────────────────────────────────

@router.get("/me", response_model=UserProfile)
async def get_my_profile(
    request: Request,
    svc: UserService = Depends(get_user_service),
):
    user = await svc.get_user(_user_id(request))
    if not user:
        raise HTTPException(404, "User not found")
    return UserProfile(
        id=str(user.id), email=user.email, phone=user.phone,
        full_name=user.full_name, display_name=user.display_name,
        avatar_url=user.avatar_url, role=user.role, status=user.status,
        language=user.language, verified_at=user.verified_at, created_at=user.created_at,
    )


@router.put("/me", response_model=UserProfile)
async def update_my_profile(
    body: UpdateProfile,
    request: Request,
    svc: UserService = Depends(get_user_service),
):
    user = await svc.update_profile(_user_id(request), **body.model_dump(exclude_unset=True))
    if not user:
        raise HTTPException(404, "User not found")
    return UserProfile(
        id=str(user.id), email=user.email, phone=user.phone,
        full_name=user.full_name, display_name=user.display_name,
        avatar_url=user.avatar_url, role=user.role, status=user.status,
        language=user.language, verified_at=user.verified_at, created_at=user.created_at,
    )


@router.get("/{user_id}", response_model=UserProfile)
async def get_user_by_id(
    user_id: str,
    request: Request,
    svc: UserService = Depends(get_user_service),
):
    if _user_role(request) not in ("admin", "super_admin"):
        raise HTTPException(403, "Admin access required")
    user = await svc.get_user(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return UserProfile(
        id=str(user.id), email=user.email, phone=user.phone,
        full_name=user.full_name, display_name=user.display_name,
        avatar_url=user.avatar_url, role=user.role, status=user.status,
        language=user.language, verified_at=user.verified_at, created_at=user.created_at,
    )


# ── Preferences ──────────────────────────────────────────────────────────────

@router.get("/me/preferences", response_model=PreferenceResponse)
async def get_preferences(
    request: Request,
    svc: UserService = Depends(get_user_service),
):
    prefs = await svc.get_preferences(_user_id(request))
    if not prefs:
        return PreferenceResponse()
    return PreferenceResponse(
        notify_push=prefs.notify_push, notify_email=prefs.notify_email,
        notify_sms=prefs.notify_sms, preferred_areas=prefs.preferred_areas or [],
        interests=prefs.interests or [],
    )


@router.put("/me/preferences", response_model=PreferenceResponse)
async def update_preferences(
    body: UpdatePreferences,
    request: Request,
    svc: UserService = Depends(get_user_service),
):
    prefs = await svc.update_preferences(_user_id(request), **body.model_dump())
    return PreferenceResponse(
        notify_push=prefs.notify_push, notify_email=prefs.notify_email,
        notify_sms=prefs.notify_sms, preferred_areas=prefs.preferred_areas or [],
        interests=prefs.interests or [],
    )


# ── KYC ──────────────────────────────────────────────────────────────────────

@router.post("/me/kyc", response_model=KYCStatusResponse, status_code=201)
async def upload_kyc(
    body: KYCUpload,
    request: Request,
    svc: UserService = Depends(get_user_service),
):
    kyc = await svc.add_kyc_document(_user_id(request), body.doc_type, body.doc_url)
    return KYCStatusResponse(
        id=str(kyc.id), doc_type=kyc.doc_type, doc_url=kyc.doc_url,
        status=kyc.status, rejection_reason=kyc.rejection_reason, created_at=kyc.created_at,
    )


@router.get("/me/kyc", response_model=list[KYCStatusResponse])
async def get_kyc_status(
    request: Request,
    svc: UserService = Depends(get_user_service),
):
    docs = await svc.get_kyc_documents(_user_id(request))
    return [
        KYCStatusResponse(
            id=str(d.id), doc_type=d.doc_type, doc_url=d.doc_url,
            status=d.status, rejection_reason=d.rejection_reason, created_at=d.created_at,
        )
        for d in docs
    ]
