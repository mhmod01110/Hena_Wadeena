"""Search request schemas."""

from pydantic import BaseModel, Field
from typing import Optional


class SearchDocumentCreate(BaseModel):
    resource_type: str = Field(..., min_length=2, max_length=50)
    resource_id: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=2, max_length=255)
    description: str = Field(..., min_length=2, max_length=3000)
    location: Optional[str] = Field(default=None, max_length=255)
    tags: list[str] = Field(default_factory=list)
    url: Optional[str] = Field(default=None, max_length=1024)