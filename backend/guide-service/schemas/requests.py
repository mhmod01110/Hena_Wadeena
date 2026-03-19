"""Guide request schemas."""

from typing import Optional

from pydantic import BaseModel, Field


BOOKING_STATUS_PATTERN = (
    "^(pending|confirmed|in_progress|completed|cancelled_tourist|cancelled_guide|no_show|cancelled)$"
)


class GuideProfileCreate(BaseModel):
    display_name: str = Field(..., min_length=2, max_length=120)
    bio: str = Field(..., min_length=10, max_length=2000)
    languages: list[str] = Field(default_factory=list)
    specialties: list[str] = Field(default_factory=list)
    operating_cities: list[str] = Field(default_factory=list)
    base_price: float = Field(..., ge=0)


class GuideProfileUpdate(BaseModel):
    display_name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    bio: Optional[str] = Field(default=None, min_length=10, max_length=2000)
    languages: Optional[list[str]] = None
    specialties: Optional[list[str]] = None
    operating_cities: Optional[list[str]] = None
    base_price: Optional[float] = Field(default=None, ge=0)
    active: Optional[bool] = None
    verified: Optional[bool] = None


class PackageCreate(BaseModel):
    guide_profile_id: str
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10, max_length=3000)
    duration_hrs: float = Field(..., gt=0, le=240)
    max_people: int = Field(..., ge=1, le=50)
    price: float = Field(..., ge=0)
    category: Optional[str] = Field(default=None, max_length=80)
    includes: list[str] = Field(default_factory=list)
    images: list[str] = Field(default_factory=list)
    active: bool = True


class PackageUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=255)
    description: Optional[str] = Field(default=None, min_length=10, max_length=3000)
    duration_hrs: Optional[float] = Field(default=None, gt=0, le=240)
    max_people: Optional[int] = Field(default=None, ge=1, le=50)
    price: Optional[float] = Field(default=None, ge=0)
    category: Optional[str] = Field(default=None, max_length=80)
    includes: Optional[list[str]] = None
    images: Optional[list[str]] = None
    active: Optional[bool] = None


class BookingCreate(BaseModel):
    guide_profile_id: str
    package_id: Optional[str] = None
    booking_date: str = Field(..., min_length=8, max_length=50)
    start_time: str = Field(..., min_length=2, max_length=20)
    duration_hrs: Optional[float] = Field(default=None, gt=0, le=240)
    people_count: int = Field(default=1, ge=1, le=30)
    notes: Optional[str] = Field(default=None, max_length=1500)


class BookingStatusUpdate(BaseModel):
    status: str = Field(..., pattern=BOOKING_STATUS_PATTERN)
    reason: Optional[str] = Field(default=None, max_length=1000)


class BookingCancelRequest(BaseModel):
    reason: Optional[str] = Field(default=None, max_length=1000)


class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(..., min_length=2, max_length=2000)


class ReviewReplyUpdate(BaseModel):
    reply: str = Field(..., min_length=2, max_length=2000)
