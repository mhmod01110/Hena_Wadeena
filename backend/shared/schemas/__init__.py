"""Common response schemas."""

from typing import Any, Optional
from pydantic import BaseModel


class APIResponse(BaseModel):
    """Standard success response wrapper."""
    success: bool = True
    message: str = "OK"
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = False
    message: str
    detail: Optional[str] = None
