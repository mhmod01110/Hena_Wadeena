"""Map service SQLAlchemy models."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Text, Float, Integer

from core.database import Base


class PointOfInterest(Base):
    __tablename__ = "pois"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="active")
    entity_kind = Column(String(32), nullable=False, default="poi", index=True)
    created_by = Column(String(64), nullable=True)

    # POI-specific fields
    name_ar = Column(String(255), nullable=True)
    name_en = Column(String(255), nullable=True)
    category = Column(String(50), nullable=True, index=True)
    address = Column(String(500), nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    phone = Column(String(50), nullable=True)

    # Carpool-specific fields
    driver_id = Column(String(64), nullable=True, index=True)
    origin_name = Column(String(255), nullable=True)
    destination_name = Column(String(255), nullable=True)
    departure_time = Column(String(50), nullable=True)
    seats_total = Column(Integer, nullable=True)
    seats_taken = Column(Integer, nullable=True, default=0)
    price_per_seat = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )