"""Investment service SQLAlchemy models."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Text, Float, Boolean

from core.database import Base


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="active")
    entity_kind = Column(String(32), nullable=False, default="opportunity", index=True)

    # Opportunity fields
    owner_id = Column(String(64), nullable=True, index=True)
    category = Column(String(80), nullable=True, index=True)
    location = Column(String(255), nullable=True, index=True)
    min_investment = Column(Float, nullable=True)
    max_investment = Column(Float, nullable=True)
    expected_roi = Column(String(120), nullable=True)
    is_verified = Column(Boolean, nullable=False, default=False)

    # Interest fields
    opportunity_id = Column(String(36), nullable=True, index=True)
    investor_id = Column(String(64), nullable=True, index=True)
    message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
