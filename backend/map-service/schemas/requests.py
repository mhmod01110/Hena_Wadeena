"""Map request schemas."""

from pydantic import BaseModel, Field
from typing import Optional


class POICreate(BaseModel):
    name_ar: str = Field(..., min_length=2, max_length=255)
    name_en: Optional[str] = Field(default=None, max_length=255)
    category: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = Field(default=None, max_length=2000)
    address: str = Field(..., min_length=2, max_length=500)
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    phone: Optional[str] = Field(default=None, max_length=50)


class POIUpdate(BaseModel):
    name_ar: Optional[str] = Field(default=None, min_length=2, max_length=255)
    name_en: Optional[str] = Field(default=None, max_length=255)
    category: Optional[str] = Field(default=None, min_length=2, max_length=50)
    description: Optional[str] = Field(default=None, max_length=2000)
    address: Optional[str] = Field(default=None, min_length=2, max_length=500)
    lat: Optional[float] = Field(default=None, ge=-90, le=90)
    lng: Optional[float] = Field(default=None, ge=-180, le=180)
    phone: Optional[str] = Field(default=None, max_length=50)


class CarpoolRideCreate(BaseModel):
    origin_name: str = Field(..., min_length=2, max_length=255)
    destination_name: str = Field(..., min_length=2, max_length=255)
    departure_time: str = Field(..., min_length=8, max_length=50)
    seats_total: int = Field(..., ge=1, le=12)
    price_per_seat: float = Field(..., ge=0)
    notes: Optional[str] = Field(default=None, max_length=1000)


class CarpoolRideJoin(BaseModel):
    seats_requested: int = Field(default=1, ge=1, le=4)