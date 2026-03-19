"""Business logic for guide profiles, packages, bookings, reviews, and availability."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from math import ceil
from typing import Optional

from interfaces.guide_profile_repository import IGuideProfileRepository
from models import GuideProfile


ACTIVE_BOOKING_STATES = {"pending", "confirmed", "in_progress"}
FINAL_BOOKING_STATES = {"completed", "cancelled_tourist", "cancelled_guide", "no_show"}


def _to_csv(values: list[str] | None) -> str:
    return ",".join(v.strip() for v in (values or []) if v and v.strip())


def _parse_dt(date_value: str, time_value: str) -> datetime:
    return datetime.strptime(f"{date_value} {time_value}", "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)


def _is_overlap(start_a: datetime, end_a: datetime, start_b: datetime, end_b: datetime) -> bool:
    return start_a < end_b and start_b < end_a


class GuideProfileService:
    def __init__(self, repository: IGuideProfileRepository):
        self._repository = repository

    @staticmethod
    def _normalize_status(value: Optional[str], default: str) -> str:
        return (value or default).strip().lower()

    async def create_profile(
        self,
        user_id: str,
        *,
        display_name: str,
        bio: str,
        languages: list[str],
        specialties: list[str],
        operating_cities: list[str],
        base_price: float,
        verified: bool,
    ) -> GuideProfile:
        existing_profiles = await self._repository.list_by_kind("guide_profile")
        if any((p.user_id or "") == user_id for p in existing_profiles):
            raise ValueError("Guide profile already exists for this user")

        entity = GuideProfile(
            title=f"guide-profile:{user_id}",
            description=bio,
            status="active",
            entity_kind="guide_profile",
            user_id=user_id,
            display_name=display_name.strip(),
            bio=bio.strip(),
            languages_csv=_to_csv(languages),
            specialties_csv=_to_csv(specialties),
            operating_cities_csv=_to_csv(operating_cities),
            base_price=float(base_price),
            active=True,
            verified=bool(verified),
            rating_avg=0,
            rating_count=0,
            total_bookings=0,
            total_earnings=0,
        )
        return await self._repository.create(entity)

    async def list_profiles(
        self,
        *,
        specialty: Optional[str] = None,
        active: Optional[bool] = True,
        verified: Optional[bool] = None,
    ) -> list[GuideProfile]:
        profiles = await self._repository.list_by_kind("guide_profile", status_filter="active")
        result: list[GuideProfile] = []
        for profile in profiles:
            if active is not None and bool(profile.active) != active:
                continue
            if verified is not None and bool(profile.verified) != verified:
                continue
            if specialty:
                specialties = [s.strip().lower() for s in (profile.specialties_csv or "").split(",") if s.strip()]
                if specialty.strip().lower() not in specialties:
                    continue
            result.append(profile)
        return result

    async def get_profile(self, profile_id: str) -> Optional[GuideProfile]:
        entity = await self._repository.get_by_id(profile_id)
        if not entity or entity.entity_kind != "guide_profile":
            return None
        return entity

    async def update_profile(
        self,
        profile_id: str,
        *,
        display_name: Optional[str] = None,
        bio: Optional[str] = None,
        languages: Optional[list[str]] = None,
        specialties: Optional[list[str]] = None,
        operating_cities: Optional[list[str]] = None,
        base_price: Optional[float] = None,
        active: Optional[bool] = None,
        verified: Optional[bool] = None,
    ) -> Optional[GuideProfile]:
        profile = await self.get_profile(profile_id)
        if not profile:
            return None

        if display_name is not None:
            profile.display_name = display_name.strip()
        if bio is not None:
            profile.bio = bio.strip()
            profile.description = bio.strip()
        if languages is not None:
            profile.languages_csv = _to_csv(languages)
        if specialties is not None:
            profile.specialties_csv = _to_csv(specialties)
        if operating_cities is not None:
            profile.operating_cities_csv = _to_csv(operating_cities)
        if base_price is not None:
            profile.base_price = float(base_price)
        if active is not None:
            profile.active = bool(active)
        if verified is not None:
            profile.verified = bool(verified)

        return await self._repository.update(profile)

    async def create_package(
        self,
        *,
        guide_profile_id: str,
        title: str,
        description: str,
        duration_hrs: float,
        max_people: int,
        price: float,
        category: Optional[str],
        includes: list[str],
        images: list[str],
        active: bool,
    ) -> GuideProfile:
        profile = await self.get_profile(guide_profile_id)
        if not profile:
            raise LookupError("Guide profile not found")

        entity = GuideProfile(
            title=f"package:{guide_profile_id}:{int(datetime.now(timezone.utc).timestamp()*1000)}",
            description=description.strip(),
            status="active",
            entity_kind="package",
            package_guide_profile_id=guide_profile_id,
            package_title=title.strip(),
            package_description=description.strip(),
            package_duration_hrs=float(duration_hrs),
            package_max_people=int(max_people),
            package_price=float(price),
            package_category=(category or "").strip() or None,
            package_includes_csv=_to_csv(includes),
            package_images_csv=_to_csv(images),
            package_active=bool(active),
        )
        return await self._repository.create(entity)

    async def list_packages(
        self,
        *,
        guide_profile_id: Optional[str] = None,
        active_only: bool = True,
    ) -> list[GuideProfile]:
        packages = await self._repository.list_by_kind("package", status_filter="active")
        result: list[GuideProfile] = []
        for package in packages:
            if guide_profile_id and package.package_guide_profile_id != guide_profile_id:
                continue
            if active_only and not bool(package.package_active):
                continue
            result.append(package)
        return result

    async def get_package(self, package_id: str) -> Optional[GuideProfile]:
        entity = await self._repository.get_by_id(package_id)
        if not entity or entity.entity_kind != "package":
            return None
        return entity

    async def update_package(
        self,
        package_id: str,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        duration_hrs: Optional[float] = None,
        max_people: Optional[int] = None,
        price: Optional[float] = None,
        category: Optional[str] = None,
        includes: Optional[list[str]] = None,
        images: Optional[list[str]] = None,
        active: Optional[bool] = None,
    ) -> Optional[GuideProfile]:
        package = await self.get_package(package_id)
        if not package:
            return None

        if title is not None:
            package.package_title = title.strip()
        if description is not None:
            package.package_description = description.strip()
            package.description = description.strip()
        if duration_hrs is not None:
            package.package_duration_hrs = float(duration_hrs)
        if max_people is not None:
            package.package_max_people = int(max_people)
        if price is not None:
            package.package_price = float(price)
        if category is not None:
            package.package_category = category.strip() or None
        if includes is not None:
            package.package_includes_csv = _to_csv(includes)
        if images is not None:
            package.package_images_csv = _to_csv(images)
        if active is not None:
            package.package_active = bool(active)

        return await self._repository.update(package)

    async def delete_package(self, package_id: str) -> bool:
        package = await self.get_package(package_id)
        if not package:
            return False
        await self._repository.delete(package)
        return True

    async def create_booking(
        self,
        *,
        tourist_id: str,
        guide_profile_id: str,
        booking_date: str,
        start_time: str,
        people_count: int,
        notes: Optional[str],
        package_id: Optional[str],
        duration_hrs: Optional[float],
    ) -> GuideProfile:
        profile = await self.get_profile(guide_profile_id)
        if not profile:
            raise LookupError("Guide profile not found")
        if not profile.active or not profile.verified:
            raise ValueError("Guide profile is not available for booking")
        if (profile.user_id or "") == tourist_id:
            raise PermissionError("You cannot book your own guide profile")

        try:
            booking_start = _parse_dt(booking_date, start_time)
        except ValueError as exc:
            raise ValueError("Invalid booking date/time format. Expected YYYY-MM-DD and HH:MM.") from exc

        if booking_start < datetime.now(timezone.utc):
            raise ValueError("Booking date/time cannot be in the past")

        package = None
        effective_duration = float(duration_hrs or 0)
        total_price = 0.0
        package_title = None

        if package_id:
            package = await self.get_package(package_id)
            if not package:
                raise LookupError("Package not found")
            if package.package_guide_profile_id != guide_profile_id:
                raise ValueError("Package does not belong to this guide")
            if not bool(package.package_active):
                raise ValueError("Package is not active")
            max_people = int(package.package_max_people or 0)
            if max_people > 0 and people_count > max_people:
                raise ValueError(f"Package supports up to {max_people} people")
            effective_duration = float(package.package_duration_hrs or 0)
            total_price = float(package.package_price or 0) * int(people_count)
            package_title = package.package_title
        else:
            if effective_duration <= 0:
                effective_duration = 8.0
            day_units = max(1, ceil(effective_duration / 8))
            total_price = float(profile.base_price or 0) * day_units * int(people_count)

        booking_end = booking_start + timedelta(hours=effective_duration)

        bookings = await self._repository.list_by_kind("booking")
        for booking in bookings:
            if booking.guide_profile_id != guide_profile_id:
                continue
            if self._normalize_status(booking.status, "") not in ACTIVE_BOOKING_STATES:
                continue
            if booking.booking_date != booking_date:
                continue
            try:
                existing_start = _parse_dt(booking.booking_date or "", booking.start_time or "00:00")
            except ValueError:
                continue
            existing_end = existing_start + timedelta(hours=float(booking.duration_hrs or 8))
            if _is_overlap(booking_start, booking_end, existing_start, existing_end):
                raise ValueError("Selected slot is not available")

        entity = GuideProfile(
            title=f"booking:{guide_profile_id}:{tourist_id}:{int(datetime.now(timezone.utc).timestamp()*1000)}",
            description=notes,
            status="pending",
            entity_kind="booking",
            guide_profile_id=guide_profile_id,
            guide_user_id=profile.user_id,
            guide_display_name=profile.display_name,
            tourist_id=tourist_id,
            package_id=package_id,
            booking_package_title=package_title,
            booking_date=booking_date,
            start_time=start_time,
            duration_hrs=effective_duration,
            people_count=int(people_count),
            total_price=float(total_price),
            payment_status="unpaid",
            notes=notes,
            review_submitted=False,
        )
        created = await self._repository.create(entity)
        await self._recompute_profile_metrics(guide_profile_id)
        return created

    async def list_bookings(
        self,
        *,
        uid: str,
        role: str,
        mine_only: bool,
        status_filter: Optional[str] = None,
    ) -> list[GuideProfile]:
        bookings = await self._repository.list_by_kind("booking")
        result: list[GuideProfile] = []
        role_norm = (role or "").strip().lower()
        for booking in bookings:
            if status_filter and self._normalize_status(booking.status, "") != status_filter:
                continue
            if mine_only and role_norm not in {"reviewer", "admin", "super_admin"}:
                if booking.tourist_id != uid and booking.guide_user_id != uid:
                    continue
            result.append(booking)
        return result

    async def get_booking(self, booking_id: str) -> Optional[GuideProfile]:
        entity = await self._repository.get_by_id(booking_id)
        if not entity or entity.entity_kind != "booking":
            return None
        return entity

    async def update_booking_status(
        self,
        booking_id: str,
        *,
        actor_id: str,
        actor_role: str,
        requested_status: str,
        reason: Optional[str] = None,
    ) -> Optional[GuideProfile]:
        booking = await self.get_booking(booking_id)
        if not booking:
            return None

        role_norm = (actor_role or "").strip().lower()
        current = self._normalize_status(booking.status, "pending")
        target = self._normalize_status(requested_status, current)
        if target == "cancelled":
            target = "cancelled_tourist" if booking.tourist_id == actor_id else "cancelled_guide"

        if current in FINAL_BOOKING_STATES:
            raise ValueError("Booking is already in a final state")

        if target == "confirmed":
            if booking.guide_user_id != actor_id and role_norm not in {"reviewer", "admin", "super_admin"}:
                raise PermissionError("Only guide owner can confirm booking")
            if current != "pending":
                raise ValueError("Only pending bookings can be confirmed")
        elif target == "in_progress":
            if booking.guide_user_id != actor_id and role_norm not in {"reviewer", "admin", "super_admin"}:
                raise PermissionError("Only guide owner can start booking")
            if current != "confirmed":
                raise ValueError("Only confirmed bookings can start")
        elif target == "completed":
            if booking.guide_user_id != actor_id and role_norm not in {"reviewer", "admin", "super_admin"}:
                raise PermissionError("Only guide owner can complete booking")
            if current != "in_progress":
                raise ValueError("Only in-progress bookings can be completed")
        elif target == "no_show":
            if booking.guide_user_id != actor_id and role_norm not in {"reviewer", "admin", "super_admin"}:
                raise PermissionError("Only guide owner can mark no-show")
            if current not in {"confirmed", "in_progress"}:
                raise ValueError("No-show can only be set for confirmed/in-progress bookings")
        elif target == "cancelled_tourist":
            if booking.tourist_id != actor_id and role_norm not in {"reviewer", "admin", "super_admin"}:
                raise PermissionError("Only the tourist can cancel as tourist")
            if current not in ACTIVE_BOOKING_STATES:
                raise ValueError("Only active bookings can be cancelled")
        elif target == "cancelled_guide":
            if booking.guide_user_id != actor_id and role_norm not in {"reviewer", "admin", "super_admin"}:
                raise PermissionError("Only the guide can cancel as guide")
            if current not in ACTIVE_BOOKING_STATES:
                raise ValueError("Only active bookings can be cancelled")
        else:
            raise ValueError("Unsupported booking status transition")

        booking.status = target

        if target in {"cancelled_tourist", "cancelled_guide"}:
            try:
                scheduled = _parse_dt(booking.booking_date or "", booking.start_time or "00:00")
                hours_until = (scheduled - datetime.now(timezone.utc)).total_seconds() / 3600.0
            except ValueError:
                hours_until = 0

            if target == "cancelled_tourist":
                refund_pct = 100.0 if hours_until > 24 else 50.0
                booking.guide_penalty = False
                booking.cancellation_actor = "tourist"
            else:
                refund_pct = 100.0
                booking.guide_penalty = True
                booking.cancellation_actor = "guide"

            booking.cancellation_refund_percent = refund_pct
            booking.cancelled_reason = reason
            booking.cancelled_at = datetime.now(timezone.utc)
            booking.payment_status = "refunded"
        elif target == "completed":
            booking.payment_status = "paid"
        elif target in {"confirmed", "in_progress"}:
            booking.payment_status = booking.payment_status or "unpaid"

        updated = await self._repository.update(booking)
        await self._recompute_profile_metrics(updated.guide_profile_id or "")
        return updated

    async def create_review_from_booking(
        self,
        *,
        booking_id: str,
        tourist_id: str,
        tourist_name: str,
        rating: int,
        comment: str,
    ) -> GuideProfile:
        booking = await self.get_booking(booking_id)
        if not booking:
            raise LookupError("Booking not found")
        if booking.tourist_id != tourist_id:
            raise PermissionError("You can review only your own booking")
        if self._normalize_status(booking.status, "") != "completed":
            raise ValueError("Only completed bookings can be reviewed")
        if booking.review_submitted:
            raise ValueError("A review was already submitted for this booking")

        reviews = await self._repository.list_by_kind("review")
        if any((r.review_booking_id or "") == booking_id for r in reviews):
            raise ValueError("A review already exists for this booking")

        review = GuideProfile(
            title=f"review:{booking.guide_profile_id}:{booking_id}",
            description=comment.strip(),
            status="active",
            entity_kind="review",
            review_guide_profile_id=booking.guide_profile_id,
            review_booking_id=booking_id,
            review_tourist_id=tourist_id,
            review_tourist_name=tourist_name.strip() or "Tourist",
            review_rating=int(rating),
            review_comment=comment.strip(),
            review_active=True,
        )
        created = await self._repository.create(review)

        booking.review_submitted = True
        await self._repository.update(booking)
        await self._recompute_profile_metrics(booking.guide_profile_id or "")
        return created

    async def list_reviews(self, guide_profile_id: str) -> list[GuideProfile]:
        reviews = await self._repository.list_by_kind("review", status_filter="active")
        return [
            review
            for review in reviews
            if review.review_guide_profile_id == guide_profile_id and bool(review.review_active)
        ]

    async def reply_review(
        self,
        review_id: str,
        *,
        actor_id: str,
        actor_role: str,
        reply: str,
    ) -> Optional[GuideProfile]:
        review = await self._repository.get_by_id(review_id)
        if not review or review.entity_kind != "review":
            return None

        role_norm = (actor_role or "").strip().lower()
        profile = await self.get_profile(review.review_guide_profile_id or "")
        guide_user_id = profile.user_id if profile else None

        if role_norm not in {"admin", "super_admin", "reviewer"} and guide_user_id != actor_id:
            raise PermissionError("Only guide owner can reply to this review")

        review.review_guide_reply = reply.strip()
        return await self._repository.update(review)

    async def get_availability(self, guide_profile_id: str, month: int, year: int) -> list[dict]:
        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12")
        if year < 2020 or year > 2200:
            raise ValueError("Year is out of range")

        bookings = await self._repository.list_by_kind("booking")
        blocked: list[dict] = []
        for booking in bookings:
            if booking.guide_profile_id != guide_profile_id:
                continue
            if self._normalize_status(booking.status, "") not in ACTIVE_BOOKING_STATES:
                continue

            try:
                start = _parse_dt(booking.booking_date or "", booking.start_time or "00:00")
            except ValueError:
                continue
            if start.month != month or start.year != year:
                continue

            end = start + timedelta(hours=float(booking.duration_hrs or 8))
            blocked.append(
                {
                    "booking_id": str(booking.id),
                    "date": booking.booking_date or "",
                    "start_time": booking.start_time or "",
                    "end_time": end.strftime("%H:%M"),
                    "status": booking.status,
                }
            )
        blocked.sort(key=lambda item: (item["date"], item["start_time"]))
        return blocked

    async def _recompute_profile_metrics(self, guide_profile_id: str) -> None:
        profile = await self.get_profile(guide_profile_id)
        if not profile:
            return

        reviews = await self._repository.list_by_kind("review", status_filter="active")
        guide_reviews = [
            review
            for review in reviews
            if review.review_guide_profile_id == guide_profile_id and bool(review.review_active)
        ]
        rating_count = len(guide_reviews)
        rating_avg = (
            round(sum(float(review.review_rating or 0) for review in guide_reviews) / rating_count, 2)
            if rating_count
            else 0.0
        )

        bookings = await self._repository.list_by_kind("booking")
        guide_bookings = [booking for booking in bookings if booking.guide_profile_id == guide_profile_id]
        total_bookings = len(guide_bookings)
        completed = [booking for booking in guide_bookings if booking.status == "completed"]
        total_earnings = round(sum(float(booking.total_price or 0) for booking in completed), 2)

        profile.rating_count = rating_count
        profile.rating_avg = rating_avg
        profile.total_bookings = total_bookings
        profile.total_earnings = total_earnings
        await self._repository.update(profile)
