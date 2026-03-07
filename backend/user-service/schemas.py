"""User service Pydantic schemas."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ── Internal (used by auth-service) ──────────────────────────────────────────

class InternalCreateUser(BaseModel):
    """Used by auth-service to create users (not exposed to clients)."""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    full_name: str
    password_hash: Optional[str] = None
    role: str = "tourist"


# ── Public Schemas ───────────────────────────────────────────────────────────

class UserProfile(BaseModel):
    """Public user profile response."""
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


class UpdateProfile(BaseModel):
    """Update profile request."""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    display_name: Optional[str] = Field(None, max_length=50)
    avatar_url: Optional[str] = None
    language: Optional[str] = Field(None, pattern="^(ar|en)$")


class UserPreferenceSchema(BaseModel):
    """User preferences."""
    notify_push: bool = True
    notify_email: bool = True
    notify_sms: bool = False
    preferred_areas: list[str] = []
    interests: list[str] = []


class KYCUpload(BaseModel):
    """KYC document upload request."""
    doc_type: str  # national_id | student_id | guide_license | commercial_register
    doc_url: str   # URL from media-service


class KYCStatus(BaseModel):
    """KYC document status response."""
    id: str
    doc_type: str
    doc_url: str
    status: str
    rejection_reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class InternalUserResponse(BaseModel):
    """Full user data returned to auth-service (includes password_hash)."""
    id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    full_name: str
    password_hash: Optional[str] = None
    role: str
    status: str

    class Config:
        from_attributes = True
