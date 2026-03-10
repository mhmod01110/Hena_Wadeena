"""User service SQLAlchemy models."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON, UniqueConstraint

from database import Base


class User(Base):
    """Core user profile."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=True)
    phone = Column(String(50), unique=True, nullable=True)
    full_name = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=True)
    avatar_url = Column(String(1024), nullable=True)
    password_hash = Column(String(255), nullable=True)  # null for OTP-only users
    role = Column(String(50), nullable=False, default="tourist")
    status = Column(String(50), nullable=False, default="active")  # active | suspended | banned
    language = Column(String(10), default="ar")  # ar | en
    verified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class UserKYC(Base):
    """KYC document uploads for verification."""
    __tablename__ = "user_kyc"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    doc_type = Column(String(50), nullable=False)  # national_id | student_id | guide_license
    doc_url = Column(String(1024), nullable=False)  # MinIO/storage path
    status = Column(String(50), default="pending")  # pending | approved | rejected
    reviewed_by = Column(String(36), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class UserPreference(Base):
    """User notification and content preferences."""
    __tablename__ = "user_preferences"

    user_id = Column(String(36), primary_key=True)
    notify_push = Column(Boolean, default=True)
    notify_email = Column(Boolean, default=True)
    notify_sms = Column(Boolean, default=False)
    preferred_areas = Column(JSON, default=list)
    interests = Column(JSON, default=list)  # tourism | investment | real_estate


class SavedItem(Base):
    """User's saved/bookmarked items."""
    __tablename__ = "saved_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    item_type = Column(String(50), nullable=False)  # listing | guide | poi | opportunity
    item_id = Column(String(36), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("user_id", "item_type", "item_id", name="uq_saved_item"),
    )
