"""Investment service SQLAlchemy models."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)

from core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class InvestmentOpportunity(Base):
    __tablename__ = "investment_opportunities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String(64), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(80), nullable=False, index=True)
    opportunity_type = Column(String(32), nullable=False, default="project", index=True)
    location = Column(String(255), nullable=False, index=True)
    min_investment = Column(Float, nullable=False)
    max_investment = Column(Float, nullable=False)
    expected_roi = Column(String(120), nullable=False)
    status = Column(String(50), nullable=False, default="pending_review", index=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    interest_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False)


class InvestmentInterest(Base):
    __tablename__ = "investment_interests"
    __table_args__ = (
        UniqueConstraint("opportunity_id", "investor_id", name="uq_interest_opportunity_investor"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    opportunity_id = Column(String(36), ForeignKey("investment_opportunities.id"), nullable=False, index=True)
    investor_id = Column(String(64), nullable=False, index=True)
    message = Column(Text, nullable=False)
    contact_name = Column(String(120), nullable=False)
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(40), nullable=False)
    company_name = Column(String(255), nullable=True)
    investor_type = Column(String(80), nullable=True)
    budget_range = Column(String(80), nullable=True)
    status = Column(String(50), nullable=False, default="submitted", index=True)
    owner_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False)


class InvestmentWatchlist(Base):
    __tablename__ = "investment_watchlists"
    __table_args__ = (
        UniqueConstraint("investor_id", "opportunity_id", name="uq_watchlist_investor_opportunity"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    investor_id = Column(String(64), nullable=False, index=True)
    opportunity_id = Column(String(36), ForeignKey("investment_opportunities.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
