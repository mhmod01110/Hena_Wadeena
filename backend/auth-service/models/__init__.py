"""Auth SQLAlchemy models — separate file per entity."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, SmallInteger, Text


from shared.core.database import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    token_hash = Column(String(255), nullable=False, unique=True)
    device_id = Column(String(255), nullable=True)
    ip_address = Column(String(50), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class OTPCode(Base):
    __tablename__ = "otp_codes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    target = Column(String(255), nullable=False)
    purpose = Column(String(50), nullable=False)
    code_hash = Column(String(255), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    attempts = Column(SmallInteger, default=0)


class AuthEvent(Base):
    __tablename__ = "auth_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=True)
    event_type = Column(String(50), nullable=False)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
