"""Search service SQLAlchemy models."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Text

from core.database import Base


class SearchDocument(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="indexed")

    resource_type = Column(String(80), nullable=False, index=True)
    resource_id = Column(String(64), nullable=False, index=True)
    location = Column(String(255), nullable=True, index=True)
    tags_csv = Column(Text, nullable=True)
    url = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )