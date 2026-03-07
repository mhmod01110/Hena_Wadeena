"""Auth response schemas — output serialization only."""

from pydantic import BaseModel
from typing import Optional


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class AuthResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[TokenResponse] = None


class UserInfo(BaseModel):
    id: str
    email: str
    phone: str
    full_name: str
    role: str
