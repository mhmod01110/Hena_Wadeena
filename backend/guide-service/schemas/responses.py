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
    base_price: float
    active: bool
    verified: bool
    created_at: datetime


class BookingResponse(BaseModel):
    id: str
    guide_profile_id: str
    guide_user_id: str
    tourist_id: str
    booking_date: str
    start_time: str
    people_count: int
    total_price: float
    notes: Optional[str] = None
    status: str
    created_at: datetime