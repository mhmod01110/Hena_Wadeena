"""Search response schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class SearchDocumentResponse(BaseModel):
    id: str
    resource_type: str
    resource_id: str
    title: str
    description: str
    location: str | None = None
    tags: list[str] = Field(default_factory=list)
    url: str | None = None
    score: float | None = None
    created_at: datetime