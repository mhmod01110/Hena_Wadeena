"""Notification response schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class NotificationResponse(BaseModel):
    id: str
    user_id: str
    type: str
    title: str
    body: str
    channel: list[str] = Field(default_factory=list)
    read_at: str | None = None
    status: str
    created_at: datetime


class PreferenceResponse(BaseModel):
    user_id: str
    notify_push: bool
    notify_email: bool
    notify_sms: bool