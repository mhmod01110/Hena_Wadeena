"""Market service SQLAlchemy models."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Text, Float, Boolean

from core.database import Base


class Listing(Base):
    __tablename__ = "listings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="active")

    owner_id = Column(String(64), nullable=False, index=True)
    listing_type = Column(String(40), nullable=False, default="sell")
    category = Column(String(80), nullable=False, index=True)
    location = Column(String(255), nullable=False, index=True)
    price = Column(Float, nullable=False)
    currency = Column(String(16), nullable=False, default="EGP")
    is_verified = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )