"""Notification request schemas."""

from pydantic import BaseModel, Field
from typing import Optional


class NotificationCreate(BaseModel):
    user_id: str
    type: str = Field(..., min_length=2, max_length=50)
    title: str = Field(..., min_length=2, max_length=255)
    body: str = Field(..., min_length=2, max_length=2000)
    channel: list[str] = Field(default_factory=lambda: ["in_app"])


class PreferenceUpdate(BaseModel):
    notify_push: bool = True
    notify_email: bool = True
    notify_sms: bool = False


class MarkReadRequest(BaseModel):
    read: bool = True