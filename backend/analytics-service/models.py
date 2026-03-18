"""Analytics service SQLAlchemy models."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String

from core.database import Base


class MetricEvent(Base):
    __tablename__ = "events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, unique=True)
    status = Column(String(50), nullable=False, default="recorded")

    event_type = Column(String(120), nullable=False, index=True)
    actor_id = Column(String(64), nullable=True, index=True)
    actor_role = Column(String(40), nullable=True, index=True)
    entity_type = Column(String(80), nullable=True, index=True)
    entity_id = Column(String(64), nullable=True, index=True)
    amount = Column(Float, nullable=True)
    city = Column(String(120), nullable=True, index=True)
    payment_method = Column(String(40), nullable=True)
    list_price = Column(Float, nullable=True)
    search_query = Column(String(255), nullable=True)
    results_count = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
