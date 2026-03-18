"""Market response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ListingResponse(BaseModel):
    id: str
    owner_id: str
    title: str
    listing_type: str
    category: str
    location: str
    price: float
    currency: str
    description: Optional[str] = None
    status: str
    is_verified: bool
    created_at: datetime


class PriceInsightResponse(BaseModel):
    location: str
    category: str
    avg_price: float
    listings_count: int