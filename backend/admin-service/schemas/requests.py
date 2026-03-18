"""Admin request schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ModerationReviewRequest(BaseModel):
    status: str = Field(..., pattern="^(approved|rejected)$")
    note: Optional[str] = Field(default=None, max_length=1000)


class SuspendUserRequest(BaseModel):
    reason: Optional[str] = Field(default=None, max_length=500)


class FeatureFlagUpdateRequest(BaseModel):
    enabled: bool
    description: Optional[str] = Field(default=None, max_length=500)
    rollout_percentage: int = Field(default=0, ge=0, le=100)
    owner_group: Optional[str] = Field(default=None, max_length=80)


class AnnouncementCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    body: str = Field(..., min_length=3, max_length=5000)
    audience: str = Field(default="all", min_length=2, max_length=80)
    status: str = Field(default="active", pattern="^(active|inactive|scheduled)$")
    priority: str = Field(default="normal", pattern="^(low|normal|high|urgent)$")
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None


class AnnouncementUpdateRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=255)
    body: Optional[str] = Field(default=None, min_length=3, max_length=5000)
    audience: Optional[str] = Field(default=None, min_length=2, max_length=80)
    status: Optional[str] = Field(default=None, pattern="^(active|inactive|scheduled)$")
    priority: Optional[str] = Field(default=None, pattern="^(low|normal|high|urgent)$")
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None


class ReportContentRequest(BaseModel):
    resource_type: str = Field(..., min_length=2, max_length=80)
    resource_id: str = Field(..., min_length=2, max_length=64)
    reason: str = Field(..., min_length=3, max_length=1000)
    subject_title: Optional[str] = Field(default=None, max_length=255)
    subject_category: Optional[str] = Field(default=None, max_length=80)
    source_service: Optional[str] = Field(default=None, max_length=80)
