"""Admin service SQLAlchemy models."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from core.database import Base


class FeatureFlag(Base):
    __tablename__ = "feature_flags"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    key = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="inactive")
    rollout_percentage = Column(Integer, nullable=False, default=0)
    owner_group = Column(String(80), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class ModerationQueue(Base):
    __tablename__ = "moderation_queue"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resource_type = Column(String(80), nullable=False)
    resource_id = Column(String(64), nullable=False)
    submitted_by = Column(String(64), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String(32), nullable=False, default="pending")
    reviewer_id = Column(String(64), nullable=True)
    review_note = Column(Text, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    subject_title = Column(String(255), nullable=True)
    subject_category = Column(String(80), nullable=True)
    source_service = Column(String(80), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(String(64), primary_key=True)
    display_name = Column(String(120), nullable=True)
    email = Column(String(255), nullable=True)
    role = Column(String(40), nullable=False, default="tourist")
    is_suspended = Column(Boolean, nullable=False, default=False)
    is_verified = Column(Boolean, nullable=False, default=False)
    suspended_reason = Column(Text, nullable=True)
    suspended_by = Column(String(64), nullable=True)
    suspended_at = Column(DateTime(timezone=True), nullable=True)
    unsuspended_by = Column(String(64), nullable=True)
    unsuspended_at = Column(DateTime(timezone=True), nullable=True)
    verified_by = Column(String(64), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    audience = Column(String(80), nullable=False, default="all")
    status = Column(String(32), nullable=False, default="active")
    priority = Column(String(20), nullable=False, default="normal")
    created_by = Column(String(64), nullable=False)
    starts_at = Column(DateTime(timezone=True), nullable=True)
    ends_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    action = Column(String(120), nullable=False)
    actor_id = Column(String(64), nullable=False)
    target_type = Column(String(80), nullable=False)
    target_id = Column(String(64), nullable=False)
    detail_status = Column(String(40), nullable=True)
    detail_reason = Column(Text, nullable=True)
    detail_note = Column(Text, nullable=True)
    detail_queue_id = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
