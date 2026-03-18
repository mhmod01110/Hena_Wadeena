"""Investment response schemas."""

from datetime import datetime

from pydantic import BaseModel


class OpportunityResponse(BaseModel):
    id: str
    owner_id: str
    title: str
    category: str
    location: str
    min_investment: float
    max_investment: float
    expected_roi: str
    description: str
    status: str
    is_verified: bool
    created_at: datetime


class InterestResponse(BaseModel):
    id: str
    opportunity_id: str
    investor_id: str
    message: str
    status: str
    created_at: datetime