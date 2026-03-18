"""Payment service SQLAlchemy models."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, String, Text

from core.database import Base


class WalletTransaction(Base):
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, unique=True)
    status = Column(String(50), nullable=False, default="completed")

    user_id = Column(String(64), nullable=False, index=True)
    tx_type = Column(String(32), nullable=False)
    direction = Column(String(16), nullable=False)
    amount = Column(Float, nullable=False)
    balance_after = Column(Float, nullable=False)
    payment_method = Column(String(40), nullable=True)
    reference_type = Column(String(50), nullable=True)
    reference_id = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
