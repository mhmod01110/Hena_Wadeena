"""Map response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class POIResponse(BaseModel):
    id: str
    name_ar: str
    name_en: Optional[str] = None
    category: str
    description: Optional[str] = None
    address: str
    lat: float
    lng: float
    phone: Optional[str] = None
    status: str
    created_at: datetime


class CarpoolRideResponse(BaseModel):
    id: str
    driver_id: str
    origin_name: str
    destination_name: str
    departure_time: str
    seats_total: int
    seats_taken: int
    price_per_seat: float
    notes: Optional[str] = None
    status: str
    created_at: datetime