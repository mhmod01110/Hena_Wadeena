"""Media request schemas."""

from pydantic import BaseModel, Field
from typing import Optional


class MediaAssetCreate(BaseModel):
    file_name: str = Field(..., min_length=1, max_length=255)
    mime_type: str = Field(..., min_length=3, max_length=120)
    size_bytes: int = Field(..., ge=1)
    checksum: Optional[str] = Field(default=None, max_length=128)


class MediaAssetComplete(BaseModel):
    url: str = Field(..., min_length=5, max_length=2048)
    status: str = Field(default="ready", pattern="^(ready|processing|failed)$")