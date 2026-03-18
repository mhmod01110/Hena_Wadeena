"""Notification service SQLAlchemy models."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Text, Boolean

from core.database import Base


class NotificationMessage(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="active")
    entity_kind = Column(String(32), nullable=False, default="notification", index=True)

    user_id = Column(String(64), nullable=False, index=True)

    # Notification payload fields
    notif_type = Column(String(80), nullable=True)
    notif_title = Column(String(255), nullable=True)
    notif_body = Column(Text, nullable=True)
    channel_csv = Column(String(255), nullable=True)
    read_at = Column(String(50), nullable=True)

    # Preferences fields
    notify_push = Column(Boolean, nullable=True)
    notify_email = Column(Boolean, nullable=True)
    notify_sms = Column(Boolean, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )