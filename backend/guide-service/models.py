"""Guide service SQLAlchemy models."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text

from core.database import Base


class GuideProfile(Base):
    __tablename__ = "profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="active", index=True)
    entity_kind = Column(String(32), nullable=False, default="guide_profile", index=True)

    # Guide profile fields
    user_id = Column(String(64), nullable=True, index=True)
    display_name = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    languages_csv = Column(Text, nullable=True)
    specialties_csv = Column(Text, nullable=True)
    operating_cities_csv = Column(Text, nullable=True)
    base_price = Column(Float, nullable=True)
    active = Column(Boolean, nullable=True, default=True)
    verified = Column(Boolean, nullable=True, default=False)
    rating_avg = Column(Float, nullable=False, default=0)
    rating_count = Column(Integer, nullable=False, default=0)
    total_bookings = Column(Integer, nullable=False, default=0)
    total_earnings = Column(Float, nullable=False, default=0)

    # Package fields
    package_guide_profile_id = Column(String(36), nullable=True, index=True)
    package_title = Column(String(255), nullable=True)
    package_description = Column(Text, nullable=True)
    package_duration_hrs = Column(Float, nullable=True)
    package_max_people = Column(Integer, nullable=True)
    package_price = Column(Float, nullable=True)
    package_category = Column(String(80), nullable=True)
    package_includes_csv = Column(Text, nullable=True)
    package_images_csv = Column(Text, nullable=True)
    package_active = Column(Boolean, nullable=True, default=True)

    # Booking fields
    guide_profile_id = Column(String(36), nullable=True, index=True)
    guide_user_id = Column(String(64), nullable=True, index=True)
    guide_display_name = Column(String(255), nullable=True)
    tourist_id = Column(String(64), nullable=True, index=True)
    package_id = Column(String(36), nullable=True, index=True)
    booking_package_title = Column(String(255), nullable=True)
    booking_date = Column(String(20), nullable=True, index=True)
    start_time = Column(String(20), nullable=True)
    duration_hrs = Column(Float, nullable=True)
    people_count = Column(Integer, nullable=True)
    total_price = Column(Float, nullable=True)
    payment_status = Column(String(40), nullable=True)
    notes = Column(Text, nullable=True)
    cancelled_reason = Column(Text, nullable=True)
    cancellation_actor = Column(String(20), nullable=True)
    cancellation_refund_percent = Column(Float, nullable=True)
    guide_penalty = Column(Boolean, nullable=True, default=False)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    review_submitted = Column(Boolean, nullable=False, default=False)

    # Review fields
    review_guide_profile_id = Column(String(36), nullable=True, index=True)
    review_booking_id = Column(String(36), nullable=True, index=True)
    review_tourist_id = Column(String(64), nullable=True, index=True)
    review_tourist_name = Column(String(255), nullable=True)
    review_rating = Column(Integer, nullable=True)
    review_comment = Column(Text, nullable=True)
    review_guide_reply = Column(Text, nullable=True)
    review_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
