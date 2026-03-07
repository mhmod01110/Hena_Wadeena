"""User response schemas."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserProfile(BaseModel):
    id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    full_name: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str
    status: str
    language: str
    verified_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PreferenceResponse(BaseModel):
    notify_push: bool = True
    notify_email: bool = True
    notify_sms: bool = False
    preferred_areas: list[str] = []
    interests: list[str] = []


class KYCStatusResponse(BaseModel):
    id: str
    doc_type: str
    doc_url: str
    status: str
    rejection_reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class InternalUserResponse(BaseModel):
    """Returned to auth-service (includes password_hash)."""
    id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    full_name: str
    password_hash: Optional[str] = None
    role: str
    status: str

    class Config:
        from_attributes = True
