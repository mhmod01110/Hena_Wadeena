"""Investment request schemas."""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class OpportunityCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    category: str = Field(..., min_length=2, max_length=80)
    opportunity_type: str = Field(default="project", min_length=3, max_length=32)
    location: str = Field(..., min_length=2, max_length=255)
    min_investment: float = Field(..., ge=0)
    max_investment: float = Field(..., ge=0)
    expected_roi: str = Field(..., min_length=2, max_length=120)
    description: str = Field(..., min_length=10, max_length=3000)


class OpportunityUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=255)
    category: Optional[str] = Field(default=None, min_length=2, max_length=80)
    opportunity_type: Optional[str] = Field(default=None, min_length=3, max_length=32)
    location: Optional[str] = Field(default=None, min_length=2, max_length=255)
    min_investment: Optional[float] = Field(default=None, ge=0)
    max_investment: Optional[float] = Field(default=None, ge=0)
    expected_roi: Optional[str] = Field(default=None, min_length=2, max_length=120)
    description: Optional[str] = Field(default=None, min_length=10, max_length=3000)
    status: Optional[str] = Field(default=None, pattern="^(pending_review|open|funded|closed)$")


class InterestCreate(BaseModel):
    message: str = Field(..., min_length=5, max_length=2000)
    contact_name: str = Field(..., min_length=2, max_length=120)
    contact_email: EmailStr
    contact_phone: str = Field(..., min_length=5, max_length=40)
    company_name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    investor_type: Optional[str] = Field(default=None, min_length=2, max_length=80)
    budget_range: Optional[str] = Field(default=None, min_length=2, max_length=80)


class InterestStatusUpdateRequest(BaseModel):
    status: str = Field(..., pattern="^(submitted|under_review|accepted|rejected|withdrawn)$")
    owner_notes: Optional[str] = Field(default=None, max_length=2000)
