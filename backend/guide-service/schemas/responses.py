"""Guide response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class GuideProfileResponse(BaseModel):
    id: str
    user_id: str
    display_name: str
    bio: str
    languages: list[str] = Field(default_factory=list)
    specialties: list[str] = Field(default_factory=list)
    operating_cities: list[str] = Field(default_factory=list)
    base_price: float
    active: bool
    verified: bool
    rating_avg: float
    rating_count: int
    total_bookings: int
    total_earnings: float = 0
    created_at: datetime


class PackageResponse(BaseModel):
    id: str
    guide_profile_id: str
    title: str
    description: str
    duration_hrs: float
    max_people: int
    price: float
    category: Optional[str] = None
    includes: list[str] = Field(default_factory=list)
    images: list[str] = Field(default_factory=list)
    active: bool
    created_at: datetime


class BookingResponse(BaseModel):
    id: str
    guide_profile_id: str
    guide_user_id: str
    guide_display_name: str = ""
    tourist_id: str
    package_id: Optional[str] = None
    package_title: Optional[str] = None
    booking_date: str
    start_time: str
    duration_hrs: float
    people_count: int
    total_price: float
    payment_status: str
    notes: Optional[str] = None
    status: str
    cancellation_actor: Optional[str] = None
    cancelled_reason: Optional[str] = None
    cancellation_refund_percent: Optional[float] = None
    guide_penalty: bool = False
    cancelled_at: Optional[datetime] = None
    review_submitted: bool = False
    created_at: datetime


class ReviewResponse(BaseModel):
    id: str
    guide_profile_id: str
    booking_id: str
    tourist_id: str
    tourist_name: str
    rating: int
    comment: str
    guide_reply: Optional[str] = None
    created_at: datetime


class AvailabilitySlotResponse(BaseModel):
    booking_id: str
    date: str
    start_time: str
    end_time: str
    status: str


class AvailabilityResponse(BaseModel):
    guide_profile_id: str
    month: int
    year: int
    blocked_slots: list[AvailabilitySlotResponse] = Field(default_factory=list)
