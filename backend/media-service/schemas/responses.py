"""Media response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MediaAssetResponse(BaseModel):
    id: str
    owner_id: str
    file_name: str
    mime_type: str
    size_bytes: int
    checksum: Optional[str] = None
    url: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
