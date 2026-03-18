"""Analytics response schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class EventIngestResponse(BaseModel):
    id: str
    event_type: str
    actor_id: str | None = None
    actor_role: str | None = None
    entity_type: str | None = None
    entity_id: str | None = None
    amount: float | None = None
    city: str | None = None
    payment_method: str | None = None
    price: float | None = None
    query: str | None = None
    results_count: int | None = None
    created_at: datetime


class ExportJobResponse(BaseModel):
    job_id: str
    status: str
    format: str
    report_type: str
    row_count: int
    output: str | dict[str, Any]
