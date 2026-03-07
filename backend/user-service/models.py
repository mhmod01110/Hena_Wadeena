"""User service SQLAlchemy models."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Boolean, DateTime, Text, ARRAY, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from database import Base


class User(Base):
    """Core user profile."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=True)
    phone = Column(String, unique=True, nullable=True)
    full_name = Column(String, nullable=False)
    display_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    password_hash = Column(String, nullable=True)  # null for OTP-only users
    role = Column(String, nullable=False, default="tourist")
    status = Column(String, nullable=False, default="active")  # active | suspended | banned
    language = Column(String, default="ar")  # ar | en
    verified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class UserKYC(Base):
    """KYC document uploads for verification."""
    __tablename__ = "user_kyc"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    doc_type = Column(String, nullable=False)  # national_id | student_id | guide_license
    doc_url = Column(String, nullable=False)  # MinIO/storage path
    status = Column(String, default="pending")  # pending | approved | rejected
    reviewed_by = Column(UUID(as_uuid=True), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class UserPreference(Base):
    """User notification and content preferences."""
    __tablename__ = "user_preferences"

    user_id = Column(UUID(as_uuid=True), primary_key=True)
    notify_push = Column(Boolean, default=True)
    notify_email = Column(Boolean, default=True)
    notify_sms = Column(Boolean, default=False)
    preferred_areas = Column(ARRAY(String), default=[])
    interests = Column(ARRAY(String), default=[])  # tourism | investment | real_estate


class SavedItem(Base):
    """User's saved/bookmarked items."""
    __tablename__ = "saved_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    item_type = Column(String, nullable=False)  # listing | guide | poi | opportunity
    item_id = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("user_id", "item_type", "item_id", name="uq_saved_item"),
    )
