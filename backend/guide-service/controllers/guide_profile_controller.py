"""HTTP controller for guides, packages, bookings, reviews, and availability."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status

from core.dependencies import get_guide_profile_service
from schemas.requests import (
    BookingCancelRequest,
    BookingCreate,
    BookingStatusUpdate,
    GuideProfileCreate,
    GuideProfileUpdate,
    PackageCreate,
    PackageUpdate,
    ReviewCreate,
    ReviewReplyUpdate,
)
from schemas.responses import (
    AvailabilityResponse,
    AvailabilitySlotResponse,
    BookingResponse,
    GuideProfileResponse,
    PackageResponse,
    ReviewResponse,
)
from services.guide_profile_service import GuideProfileService


router = APIRouter()

GUIDE_ROLES = {"guide", "admin", "super_admin"}
REVIEW_ROLES = {"reviewer", "admin", "super_admin"}


def _envelope(data: Any = None, meta: Optional[dict] = None, error: Optional[str] = None, success: bool = True) -> dict:
    return {"success": success, "data": data, "meta": meta, "error": error}


def _user_id(request: Request) -> str:
    uid = request.headers.get("X-User-Id")
    if not uid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")
    return uid


def _user_role(request: Request) -> str:
    return request.headers.get("X-User-Role", "tourist")


def _parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _raise_from_error(exc: Exception) -> None:
    if isinstance(exc, PermissionError):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    if isinstance(exc, LookupError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    if isinstance(exc, ValueError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    raise exc


def _to_profile(entity) -> GuideProfileResponse:
    return GuideProfileResponse(
        id=str(entity.id),
        user_id=entity.user_id or "",
        display_name=entity.display_name or "",
        bio=entity.bio or "",
        languages=_parse_csv(entity.languages_csv),
        specialties=_parse_csv(entity.specialties_csv),
        operating_cities=_parse_csv(entity.operating_cities_csv),
        base_price=float(entity.base_price or 0),
        active=bool(entity.active),
        verified=bool(entity.verified),
        rating_avg=float(entity.rating_avg or 0),
        rating_count=int(entity.rating_count or 0),
        total_bookings=int(entity.total_bookings or 0),
        total_earnings=float(entity.total_earnings or 0),
        created_at=entity.created_at,
    )


def _to_package(entity) -> PackageResponse:
    return PackageResponse(
        id=str(entity.id),
        guide_profile_id=entity.package_guide_profile_id or "",
        title=entity.package_title or "",
        description=entity.package_description or "",
        duration_hrs=float(entity.package_duration_hrs or 0),
        max_people=int(entity.package_max_people or 1),
        price=float(entity.package_price or 0),
        category=entity.package_category,
        includes=_parse_csv(entity.package_includes_csv),
        images=_parse_csv(entity.package_images_csv),
        active=bool(entity.package_active),
        created_at=entity.created_at,
    )


def _to_booking(entity) -> BookingResponse:
    return BookingResponse(
        id=str(entity.id),
        guide_profile_id=entity.guide_profile_id or "",
        guide_user_id=entity.guide_user_id or "",
        guide_display_name=entity.guide_display_name or "",
        tourist_id=entity.tourist_id or "",
        package_id=entity.package_id,
        package_title=entity.booking_package_title,
        booking_date=entity.booking_date or "",
        start_time=entity.start_time or "",
        duration_hrs=float(entity.duration_hrs or 8),
        people_count=int(entity.people_count or 1),
        total_price=float(entity.total_price or 0),
        payment_status=entity.payment_status or "unpaid",
        notes=entity.notes,
        status=entity.status,
        cancellation_actor=entity.cancellation_actor,
        cancelled_reason=entity.cancelled_reason,
        cancellation_refund_percent=entity.cancellation_refund_percent,
        guide_penalty=bool(entity.guide_penalty),
        cancelled_at=entity.cancelled_at,
        review_submitted=bool(entity.review_submitted),
        created_at=entity.created_at,
    )


def _to_review(entity) -> ReviewResponse:
    tourist_name = (entity.review_tourist_name or "").strip() or f"Tourist {str(entity.review_tourist_id or '')[:6]}"
    return ReviewResponse(
        id=str(entity.id),
        guide_profile_id=entity.review_guide_profile_id or "",
        booking_id=entity.review_booking_id or "",
        tourist_id=entity.review_tourist_id or "",
        tourist_name=tourist_name,
        rating=int(entity.review_rating or 0),
        comment=entity.review_comment or "",
        guide_reply=entity.review_guide_reply,
        created_at=entity.created_at,
    )


@router.post("/api/v1/guides/profiles", status_code=status.HTTP_201_CREATED)
async def create_profile(
    body: GuideProfileCreate,
    request: Request,
    service: GuideProfileService = Depends(get_guide_profile_service),
):
    role = _user_role(request)
    if role not in GUIDE_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only guides can create profiles")
    user_id = _user_id(request)

    try:
        profile = await service.create_profile(
            user_id=user_id,
            display_name=body.display_name,
            bio=body.bio,
            languages=body.languages,
            specialties=body.specialties,
            operating_cities=body.operating_cities,
            base_price=body.base_price,
            verified=role in REVIEW_ROLES,
        )
    except Exception as exc:  # noqa: BLE001
        _raise_from_error(exc)

    return _envelope(_to_profile(profile).model_dump())


@router.get("/api/v1/guides/profiles")
async def list_profiles(
    specialty: Optional[str] = Query(default=None),
    active: Optional[bool] = Query(default=True),
    verified: Optional[bool] = Query(default=None),
    service: GuideProfileService = Depends(get_guide_profile_service),
):
    profiles = await service.list_profiles(specialty=specialty, active=active, verified=verified)
    payload = [_to_profile(profile).model_dump() for profile in profiles]
    return _envelope(payload, meta={"total": len(payload)})


@router.get("/api/v1/guides/profiles/{profile_id}")
async def get_profile(
    profile_id: str,
    service: GuideProfileService = Depends(get_guide_profile_service),
):
    profile = await service.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guide profile not found")
    return _envelope(_to_profile(profile).model_dump())


@router.patch("/api/v1/guides/profiles/{profile_id}")
async def update_profile(
    profile_id: str,
    body: GuideProfileUpdate,
    request: Request,
    service: GuideProfileService = Depends(get_guide_profile_service),
):
    profile = await service.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guide profile not found")

    role = _user_role(request)
    user_id = _user_id(request)
    if role not in REVIEW_ROLES and profile.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to update this profile")

    patch = body.model_dump(exclude_unset=True)
    if role not in REVIEW_ROLES:
        patch.pop("verified", None)

    try:
        updated = await service.update_profile(profile_id, **patch)
    except Exception as exc:  # noqa: BLE001
        _raise_from_error(exc)

    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guide profile not found")
    return _envelope(_to_profile(updated).model_dump())


@router.get("/api/v1/guides/profiles/{profile_id}/packages")
async def list_profile_packages(
    profile_id: str,
    include_inactive: bool = Query(default=False),
    service: GuideProfileService = Depends(get_guide_profile_service),
):
    profile = await service.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guide profile not found")
    packages = await service.list_packages(guide_profile_id=profile_id, active_only=not include_inactive)
    payload = [_to_package(package).model_dump() for package in packages]
    return _envelope(payload, meta={"total": len(payload)})


@router.post("/api/v1/guides/packages", status_code=status.HTTP_201_CREATED)
async def create_package(
    body: PackageCreate,
    request: Request,
    service: GuideProfileService = Depends(get_guide_profile_service),
):
    uid = _user_id(request)
    role = _user_role(request)
    if role not in GUIDE_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only guides can create packages")

    profile = await service.get_profile(body.guide_profile_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guide profile not found")
    if role not in REVIEW_ROLES and profile.user_id != uid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed for this profile")

    try:
        package = await service.create_package(
            guide_profile_id=body.guide_profile_id,
            title=body.title,
            description=body.description,
            duration_hrs=body.duration_hrs,
            max_people=body.max_people,
            price=body.price,
            category=body.category,
            includes=body.includes,
            images=body.images,
            active=body.active,
        )
    except Exception as exc:  # noqa: BLE001
        _raise_from_error(exc)

    return _envelope(_to_package(package).model_dump())


@router.patch("/api/v1/guides/packages/{package_id}")
async def update_package(
    package_id: str,
    body: PackageUpdate,
    request: Request,
    service: GuideProfileService = Depends(get_guide_profile_service),
):
    uid = _user_id(request)
    role = _user_role(request)
    package = await service.get_package(package_id)
    if not package:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Package not found")

    profile = await service.get_profile(package.package_guide_profile_id or "")
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guide profile not found")
    if role not in REVIEW_ROLES and profile.user_id != uid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed for this package")

    try:
        updated = await service.update_package(package_id, **body.model_dump(exclude_unset=True))
    except Exception as exc:  # noqa: BLE001
        _raise_from_error(exc)

    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Package not found")
    return _envelope(_to_package(updated).model_dump())


@router.delete("/api/v1/guides/packages/{package_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_package(
    package_id: str,
    request: Request,
    service: GuideProfileService = Depends(get_guide_profile_service),
):
    uid = _user_id(request)
    role = _user_role(request)

    package = await service.get_package(package_id)
    if not package:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Package not found")

    profile = await service.get_profile(package.package_guide_profile_id or "")
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guide profile not found")
    if role not in REVIEW_ROLES and profile.user_id != uid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed for this package")

    await service.delete_package(package_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/api/v1/guides/profiles/{profile_id}/reviews")
async def list_reviews(
    profile_id: str,
    service: GuideProfileService = Depends(get_guide_profile_service),
):
    profile = await service.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guide profile not found")
    reviews = await service.list_reviews(profile_id)
    payload = [_to_review(review).model_dump() for review in reviews]
    return _envelope(payload, meta={"total": len(payload)})


@router.post("/api/v1/bookings/{booking_id}/review", status_code=status.HTTP_201_CREATED)
async def create_review_from_booking(
    booking_id: str,
    body: ReviewCreate,
    request: Request,
    service: GuideProfileService = Depends(get_guide_profile_service),
):
    role = _user_role(request)
    if role != "tourist":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only tourists can submit reviews")
    uid = _user_id(request)

    try:
        review = await service.create_review_from_booking(
            booking_id=booking_id,
            tourist_id=uid,
            tourist_name=request.headers.get("X-User-Name", "Tourist"),
            rating=body.rating,
            comment=body.comment,
        )
    except Exception as exc:  # noqa: BLE001
        _raise_from_error(exc)

    return _envelope(_to_review(review).model_dump())


@router.patch("/api/v1/guides/reviews/{review_id}/reply")
async def reply_review(
    review_id: str,
    body: ReviewReplyUpdate,
    request: Request,
    service: GuideProfileService = Depends(get_guide_profile_service),
):
    uid = _user_id(request)
    role = _user_role(request)

    try:
        updated = await service.reply_review(review_id, actor_id=uid, actor_role=role, reply=body.reply)
    except Exception as exc:  # noqa: BLE001
        _raise_from_error(exc)

    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    return _envelope(_to_review(updated).model_dump())


@router.get("/api/v1/guides/profiles/{profile_id}/availability")
async def get_availability(
    profile_id: str,
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2020, le=2200),
    service: GuideProfileService = Depends(get_guide_profile_service),
):
    profile = await service.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guide profile not found")

    try:
        blocked = await service.get_availability(profile_id, month=month, year=year)
    except Exception as exc:  # noqa: BLE001
        _raise_from_error(exc)

    response = AvailabilityResponse(
        guide_profile_id=profile_id,
        month=month,
        year=year,
        blocked_slots=[AvailabilitySlotResponse(**slot) for slot in blocked],
    )
    return _envelope(response.model_dump())


@router.post("/api/v1/bookings", status_code=status.HTTP_201_CREATED)
async def create_booking(
    body: BookingCreate,
    request: Request,
    service: GuideProfileService = Depends(get_guide_profile_service),
):
    uid = _user_id(request)

    try:
        booking = await service.create_booking(
            tourist_id=uid,
            guide_profile_id=body.guide_profile_id,
            package_id=body.package_id,
            booking_date=body.booking_date,
            start_time=body.start_time,
            duration_hrs=body.duration_hrs,
            people_count=body.people_count,
            notes=body.notes,
        )
    except Exception as exc:  # noqa: BLE001
        _raise_from_error(exc)

    return _envelope(_to_booking(booking).model_dump())


@router.get("/api/v1/bookings")
async def list_bookings(
    request: Request,
    mine_only: bool = Query(default=True),
    status_filter: Optional[str] = Query(default=None, alias="status"),
    service: GuideProfileService = Depends(get_guide_profile_service),
):
    uid = _user_id(request)
    role = _user_role(request)
    bookings = await service.list_bookings(uid=uid, role=role, mine_only=mine_only, status_filter=status_filter)
    payload = [_to_booking(booking).model_dump() for booking in bookings]
    return _envelope(payload, meta={"total": len(payload)})


@router.patch("/api/v1/bookings/{booking_id}/status")
async def update_booking_status(
    booking_id: str,
    body: BookingStatusUpdate,
    request: Request,
    service: GuideProfileService = Depends(get_guide_profile_service),
):
    uid = _user_id(request)
    role = _user_role(request)
    try:
        updated = await service.update_booking_status(
            booking_id,
            actor_id=uid,
            actor_role=role,
            requested_status=body.status,
            reason=body.reason,
        )
    except Exception as exc:  # noqa: BLE001
        _raise_from_error(exc)

    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return _envelope(_to_booking(updated).model_dump())


@router.get("/api/v1/guides/bookings/my")
async def list_my_bookings_alias(
    request: Request,
    status_filter: Optional[str] = Query(default=None, alias="status"),
    service: GuideProfileService = Depends(get_guide_profile_service),
):
    uid = _user_id(request)
    role = _user_role(request)
    bookings = await service.list_bookings(uid=uid, role=role, mine_only=True, status_filter=status_filter)
    payload = [_to_booking(booking).model_dump() for booking in bookings]
    return _envelope(payload, meta={"total": len(payload)})


@router.patch("/api/v1/guides/bookings/{booking_id}/confirm")
async def confirm_booking(
    booking_id: str,
    request: Request,
    service: GuideProfileService = Depends(get_guide_profile_service),
):
    uid = _user_id(request)
    role = _user_role(request)
    try:
        updated = await service.update_booking_status(
            booking_id, actor_id=uid, actor_role=role, requested_status="confirmed", reason=None
        )
    except Exception as exc:  # noqa: BLE001
        _raise_from_error(exc)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return _envelope(_to_booking(updated).model_dump())


@router.patch("/api/v1/guides/bookings/{booking_id}/start")
async def start_booking(
    booking_id: str,
    request: Request,
    service: GuideProfileService = Depends(get_guide_profile_service),
):
    uid = _user_id(request)
    role = _user_role(request)
    try:
        updated = await service.update_booking_status(
            booking_id, actor_id=uid, actor_role=role, requested_status="in_progress", reason=None
        )
    except Exception as exc:  # noqa: BLE001
        _raise_from_error(exc)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return _envelope(_to_booking(updated).model_dump())


@router.patch("/api/v1/guides/bookings/{booking_id}/complete")
async def complete_booking(
    booking_id: str,
    request: Request,
    service: GuideProfileService = Depends(get_guide_profile_service),
):
    uid = _user_id(request)
    role = _user_role(request)
    try:
        updated = await service.update_booking_status(
            booking_id, actor_id=uid, actor_role=role, requested_status="completed", reason=None
        )
    except Exception as exc:  # noqa: BLE001
        _raise_from_error(exc)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return _envelope(_to_booking(updated).model_dump())


@router.patch("/api/v1/guides/bookings/{booking_id}/no-show")
async def mark_no_show(
    booking_id: str,
    request: Request,
    service: GuideProfileService = Depends(get_guide_profile_service),
):
    uid = _user_id(request)
    role = _user_role(request)
    try:
        updated = await service.update_booking_status(
            booking_id, actor_id=uid, actor_role=role, requested_status="no_show", reason=None
        )
    except Exception as exc:  # noqa: BLE001
        _raise_from_error(exc)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return _envelope(_to_booking(updated).model_dump())


@router.patch("/api/v1/guides/bookings/{booking_id}/cancel")
async def cancel_booking(
    booking_id: str,
    body: BookingCancelRequest,
    request: Request,
    service: GuideProfileService = Depends(get_guide_profile_service),
):
    uid = _user_id(request)
    role = _user_role(request)
    desired = "cancelled_tourist" if role == "tourist" else "cancelled_guide"
    try:
        updated = await service.update_booking_status(
            booking_id,
            actor_id=uid,
            actor_role=role,
            requested_status=desired,
            reason=body.reason,
        )
    except Exception as exc:  # noqa: BLE001
        _raise_from_error(exc)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return _envelope(_to_booking(updated).model_dump())
