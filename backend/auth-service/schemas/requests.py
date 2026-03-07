"""Auth request schemas — input validation only."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class RegisterRequest(BaseModel):
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=6, max_length=128)
    role: str = "tourist"


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
