"""Investment response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class OpportunityResponse(BaseModel):
    id: str
    owner_id: str
    title: str
    category: str
    opportunity_type: str
    location: str
    min_investment: float
    max_investment: float
    investment_range: str
    expected_roi: str
    description: str
    status: str
    is_verified: bool
    interest_count: int
    is_watchlisted: bool
    created_at: datetime
    updated_at: datetime


class InterestResponse(BaseModel):
    id: str
    opportunity_id: str
    opportunity_title: Optional[str] = None
    opportunity_category: Optional[str] = None
    opportunity_location: Optional[str] = None
    opportunity_type: Optional[str] = None
    investor_id: str
    message: str
    contact_name: str
    contact_email: str
    contact_phone: str
    company_name: Optional[str] = None
    investor_type: Optional[str] = None
    budget_range: Optional[str] = None
    status: str
    owner_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class InvestorDashboardResponse(BaseModel):
    status_counts: dict[str, int]
    recent_interests: list[InterestResponse]
    watchlist: list[OpportunityResponse]
    recommended: list[OpportunityResponse]
