"""User request schemas."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class RegisterDocument(BaseModel):
    doc_type: str = Field(..., min_length=2, max_length=50)
    file_name: str = Field(..., min_length=1, max_length=255)
    mime_type: Optional[str] = Field(None, max_length=100)
    size_bytes: Optional[int] = Field(None, ge=0)


class InternalCreateUser(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    full_name: str
    password_hash: Optional[str] = None
    role: str = "tourist"
    city: Optional[str] = Field(None, max_length=100)
    organization: Optional[str] = Field(None, max_length=255)
    documents: list[RegisterDocument] = Field(default_factory=list)


class UpdateProfile(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    display_name: Optional[str] = Field(None, max_length=50)
    avatar_url: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    organization: Optional[str] = Field(None, max_length=255)
    language: Optional[str] = Field(None, pattern="^(ar|en)$")


class UpdatePreferences(BaseModel):
    notify_push: bool = True
    notify_email: bool = True
    notify_sms: bool = False
    preferred_areas: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)


class KYCUpload(BaseModel):
    doc_type: str
    doc_url: str
