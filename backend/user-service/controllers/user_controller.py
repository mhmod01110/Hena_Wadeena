"""
Public user controller.
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


def _user_profile_response(user) -> UserProfile:
    return UserProfile(
        id=str(user.id),
        email=user.email,
        phone=user.phone,
        full_name=user.full_name,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        city=user.city,
        organization=user.organization,
        role=user.role,
        status=user.status,
        language=user.language,
        verified_at=user.verified_at,
        created_at=user.created_at,
    )


@router.get("/me", response_model=UserProfile)
async def get_my_profile(
    request: Request,
    svc: UserService = Depends(get_user_service),
):
    user = await svc.get_user(_user_id(request))
    if not user:
        raise HTTPException(404, "User not found")
    return _user_profile_response(user)


@router.put("/me", response_model=UserProfile)
async def update_my_profile(
    body: UpdateProfile,
    request: Request,
    svc: UserService = Depends(get_user_service),
):
    try:
        user = await svc.update_profile(_user_id(request), **body.model_dump(exclude_unset=True))
    except ValueError as exc:
        raise HTTPException(409, str(exc))

    if not user:
        raise HTTPException(404, "User not found")
    return _user_profile_response(user)


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
    return _user_profile_response(user)


@router.get("/me/preferences", response_model=PreferenceResponse)
async def get_preferences(
    request: Request,
    svc: UserService = Depends(get_user_service),
):
    prefs = await svc.get_preferences(_user_id(request))
    if not prefs:
        return PreferenceResponse()

    return PreferenceResponse(
        notify_push=prefs.notify_push,
        notify_email=prefs.notify_email,
        notify_sms=prefs.notify_sms,
        preferred_areas=prefs.preferred_areas or [],
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
        notify_push=prefs.notify_push,
        notify_email=prefs.notify_email,
        notify_sms=prefs.notify_sms,
        preferred_areas=prefs.preferred_areas or [],
        interests=prefs.interests or [],
    )


@router.post("/me/kyc", response_model=KYCStatusResponse, status_code=201)
async def upload_kyc(
    body: KYCUpload,
    request: Request,
    svc: UserService = Depends(get_user_service),
):
    kyc = await svc.add_kyc_document(_user_id(request), body.doc_type, body.doc_url)
    return KYCStatusResponse(
        id=str(kyc.id),
        doc_type=kyc.doc_type,
        doc_url=kyc.doc_url,
        status=kyc.status,
        rejection_reason=kyc.rejection_reason,
        created_at=kyc.created_at,
    )


@router.get("/me/kyc", response_model=list[KYCStatusResponse])
async def get_kyc_status(
    request: Request,
    svc: UserService = Depends(get_user_service),
):
    docs = await svc.get_kyc_documents(_user_id(request))
    return [
        KYCStatusResponse(
            id=str(doc.id),
            doc_type=doc.doc_type,
            doc_url=doc.doc_url,
            status=doc.status,
            rejection_reason=doc.rejection_reason,
            created_at=doc.created_at,
        )
        for doc in docs
    ]
