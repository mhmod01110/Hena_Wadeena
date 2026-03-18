"""Market request schemas."""

from pydantic import BaseModel, Field
from typing import Optional, Literal


class ListingCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    listing_type: Literal["sell", "rent", "land", "commercial"] = "sell"
    category: str = Field(..., min_length=2, max_length=50)
    location: str = Field(..., min_length=2, max_length=255)
    price: float = Field(..., ge=0)
    currency: str = Field(default="EGP", min_length=3, max_length=3)
    description: Optional[str] = Field(default=None, max_length=2000)


class ListingUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=255)
    listing_type: Optional[Literal["sell", "rent", "land", "commercial"]] = None
    category: Optional[str] = Field(default=None, min_length=2, max_length=50)
    location: Optional[str] = Field(default=None, min_length=2, max_length=255)
    price: Optional[float] = Field(default=None, ge=0)
    currency: Optional[str] = Field(default=None, min_length=3, max_length=3)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: Optional[str] = Field(default=None, min_length=2, max_length=50)