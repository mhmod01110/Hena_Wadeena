"""Analytics request schemas."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class EventIngestRequest(BaseModel):
    event_type: str = Field(..., min_length=3, max_length=120)
    actor_id: Optional[str] = Field(default=None, max_length=64)
    actor_role: Optional[str] = Field(default=None, max_length=40)
    entity_type: Optional[str] = Field(default=None, max_length=80)
    entity_id: Optional[str] = Field(default=None, max_length=64)
    amount: Optional[float] = Field(default=None, ge=0)
    city: Optional[str] = Field(default=None, max_length=120)
    payment_method: Optional[str] = Field(default=None, max_length=40)
    price: Optional[float] = Field(default=None, ge=0)
    query: Optional[str] = Field(default=None, max_length=255)
    results_count: Optional[int] = Field(default=None, ge=0)
    occurred_at: Optional[datetime] = None


class ExportRequest(BaseModel):
    report_type: str = Field(
        default="kpis",
        pattern="^(overview|users|listings|bookings|revenue|search|market_heatmap|kpis)$",
    )
    date_from: date
    date_to: date
    format: str = Field(default="csv", pattern="^(csv|json)$")
