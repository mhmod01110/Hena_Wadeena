"""Auth service SQLAlchemy models."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, SmallInteger, Text
from sqlalchemy.dialects.postgresql import UUID, INET

from database import Base


class RefreshToken(Base):
    """Stored refresh tokens for session management."""
    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    token_hash = Column(String, nullable=False, unique=True)
    device_id = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class OTPCode(Base):
    """OTP codes for phone/email verification."""
    __tablename__ = "otp_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    target = Column(String, nullable=False)  # phone or email
    purpose = Column(String, nullable=False)  # login | reset | verify
    code_hash = Column(String, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    attempts = Column(SmallInteger, default=0)


class AuthEvent(Base):
    """Audit log for authentication events."""
    __tablename__ = "auth_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    event_type = Column(String, nullable=False)  # login | logout | failed | register
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
