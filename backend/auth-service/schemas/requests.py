"""Auth request schemas."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class RegisterDocument(BaseModel):
    doc_type: str = Field(..., min_length=2, max_length=50)
    file_name: str = Field(..., min_length=1, max_length=255)
    mime_type: Optional[str] = Field(None, max_length=100)
    size_bytes: Optional[int] = Field(None, ge=0)


class RegisterRequest(BaseModel):
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=6, max_length=128)
    role: str = "tourist"
    city: Optional[str] = Field(None, max_length=100)
    organization: Optional[str] = Field(None, max_length=255)
    documents: list[RegisterDocument] = Field(default_factory=list)


class LoginRequest(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class OTPRequestSchema(BaseModel):
    phone: str = Field(..., min_length=10, max_length=15)
    purpose: str = "login"


class OTPVerifySchema(BaseModel):
    phone: str = Field(..., min_length=10, max_length=15)
    code: str = Field(..., min_length=6, max_length=6)
