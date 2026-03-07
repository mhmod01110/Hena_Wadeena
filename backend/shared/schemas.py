"""Shared Pydantic schemas used across services."""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel


class UserRole(str, Enum):
    TOURIST = "tourist"
    STUDENT = "student"
    INVESTOR = "investor"
    LOCAL_CITIZEN = "local_citizen"
    GUIDE = "guide"
    MERCHANT = "merchant"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class UserStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"


class APIResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool = True
    message: str = "OK"
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = False
    message: str
    detail: Optional[str] = None


class TokenPayload(BaseModel):
    """Decoded JWT payload."""
    sub: str  # user_id
    role: str
    jti: str
    exp: int
    iat: int
    type: str = "access"
