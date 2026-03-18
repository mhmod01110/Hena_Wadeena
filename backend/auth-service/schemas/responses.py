"""Auth response schemas."""

from pydantic import BaseModel
from typing import Optional


class UserInfo(BaseModel):
    id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    full_name: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    city: Optional[str] = None
    organization: Optional[str] = None
    role: str
    status: str
    language: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserInfo


class AuthResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[TokenResponse] = None
