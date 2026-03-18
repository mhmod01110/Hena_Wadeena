"""Investment request schemas."""

from pydantic import BaseModel, Field
from typing import Optional


class OpportunityCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    category: str = Field(..., min_length=2, max_length=80)
    location: str = Field(..., min_length=2, max_length=255)
    min_investment: float = Field(..., ge=0)
    max_investment: float = Field(..., ge=0)
    expected_roi: str = Field(..., min_length=2, max_length=40)
    description: str = Field(..., min_length=10, max_length=3000)


class OpportunityUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=255)
    category: Optional[str] = Field(default=None, min_length=2, max_length=80)
    location: Optional[str] = Field(default=None, min_length=2, max_length=255)
    min_investment: Optional[float] = Field(default=None, ge=0)
    max_investment: Optional[float] = Field(default=None, ge=0)
    expected_roi: Optional[str] = Field(default=None, min_length=2, max_length=40)
    description: Optional[str] = Field(default=None, min_length=10, max_length=3000)
    status: Optional[str] = Field(default=None, pattern="^(open|closed|draft|under_review)$")


class InterestCreate(BaseModel):
    opportunity_id: str
    message: str = Field(..., min_length=5, max_length=1000)