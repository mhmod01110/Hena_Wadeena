"""User request schemas."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class InternalCreateUser(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    full_name: str
    password_hash: Optional[str] = None
    role: str = "tourist"


class UpdateProfile(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    display_name: Optional[str] = Field(None, max_length=50)
    avatar_url: Optional[str] = None
    language: Optional[str] = Field(None, pattern="^(ar|en)$")


class UpdatePreferences(BaseModel):
    notify_push: bool = True
    notify_email: bool = True
    notify_sms: bool = False
    preferred_areas: list[str] = []
    interests: list[str] = []


class KYCUpload(BaseModel):
    doc_type: str
    doc_url: str
