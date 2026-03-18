"""Admin response schemas."""

from datetime import datetime

from pydantic import BaseModel


class ModerationQueueResponse(BaseModel):
    id: str
    resource_type: str
    resource_id: str
    submitted_by: str
    reason: str
    status: str
    reviewer_id: str | None = None
    review_note: str | None = None
    reviewed_at: datetime | None = None
    subject_title: str | None = None
    subject_category: str | None = None
    source_service: str | None = None
    created_at: datetime
    updated_at: datetime


class AdminUserResponse(BaseModel):
    id: str
    display_name: str | None = None
    email: str | None = None
    role: str
    is_suspended: bool
    is_verified: bool
    suspended_reason: str | None = None
    suspended_by: str | None = None
    suspended_at: datetime | None = None
    unsuspended_by: str | None = None
    unsuspended_at: datetime | None = None
    verified_by: str | None = None
    verified_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class FeatureFlagResponse(BaseModel):
    key: str
    enabled: bool
    description: str | None = None
    rollout_percentage: int
    owner_group: str | None = None
    updated_at: datetime


class AuditLogResponse(BaseModel):
    id: str
    action: str
    actor_id: str
    target_type: str
    target_id: str
    detail_status: str | None = None
    detail_reason: str | None = None
    detail_note: str | None = None
    detail_queue_id: str | None = None
    created_at: datetime


class AnnouncementResponse(BaseModel):
    id: str
    title: str
    body: str
    audience: str
    status: str
    priority: str
    created_by: str
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
