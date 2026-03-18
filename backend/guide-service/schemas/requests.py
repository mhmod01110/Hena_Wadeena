"""Guide request schemas."""

from pydantic import BaseModel, Field
from typing import Optional


class GuideProfileCreate(BaseModel):
    display_name: str = Field(..., min_length=2, max_length=120)
    bio: str = Field(..., min_length=10, max_length=2000)
    languages: list[str] = Field(default_factory=list)
    specialties: list[str] = Field(default_factory=list)
    base_price: float = Field(..., ge=0)


class GuideProfileUpdate(BaseModel):
    display_name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    bio: Optional[str] = Field(default=None, min_length=10, max_length=2000)
    languages: Optional[list[str]] = None
    specialties: Optional[list[str]] = None
    base_price: Optional[float] = Field(default=None, ge=0)
    active: Optional[bool] = None


class BookingCreate(BaseModel):
    guide_profile_id: str
    booking_date: str = Field(..., min_length=8, max_length=50)
    start_time: str = Field(..., min_length=2, max_length=20)
    people_count: int = Field(default=1, ge=1, le=30)
    notes: Optional[str] = Field(default=None, max_length=1000)


class BookingStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(pending|confirmed|completed|cancelled)$")