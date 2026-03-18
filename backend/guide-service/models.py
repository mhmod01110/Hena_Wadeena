"""Guide service SQLAlchemy models."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Text, Float, Integer, Boolean

from core.database import Base


class GuideProfile(Base):
    __tablename__ = "profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="active")
    entity_kind = Column(String(32), nullable=False, default="guide_profile", index=True)

    # Guide profile fields
    user_id = Column(String(64), nullable=True, index=True)
    display_name = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    languages_csv = Column(Text, nullable=True)
    specialties_csv = Column(Text, nullable=True)
    base_price = Column(Float, nullable=True)
    active = Column(Boolean, nullable=True, default=True)
    verified = Column(Boolean, nullable=True, default=False)

    # Booking fields
    guide_profile_id = Column(String(36), nullable=True, index=True)
    guide_user_id = Column(String(64), nullable=True, index=True)
    tourist_id = Column(String(64), nullable=True, index=True)
    booking_date = Column(String(20), nullable=True)
    start_time = Column(String(20), nullable=True)
    people_count = Column(Integer, nullable=True)
    total_price = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )