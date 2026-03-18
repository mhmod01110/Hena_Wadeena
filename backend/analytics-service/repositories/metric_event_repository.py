"""SQLAlchemy repository for analytics event store."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import MetricEvent


class SqlAlchemyMetricEventRepository:

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_event(self, event: MetricEvent) -> MetricEvent:
        self._session.add(event)
        await self._session.flush()
        await self._session.refresh(event)
        return event

    async def list_events(
        self,
        *,
        date_from: datetime,
        date_to: datetime,
        limit: Optional[int] = None,
    ) -> list[MetricEvent]:
        if date_from.tzinfo is None:
            date_from = date_from.replace(tzinfo=timezone.utc)
        if date_to.tzinfo is None:
            date_to = date_to.replace(tzinfo=timezone.utc)

        query = (
            select(MetricEvent)
            .where(MetricEvent.created_at >= date_from)
            .where(MetricEvent.created_at <= date_to)
            .order_by(MetricEvent.created_at.desc())
        )
        if limit is not None:
            query = query.limit(limit)

        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_event(self, event_id: str) -> Optional[MetricEvent]:
        result = await self._session.execute(select(MetricEvent).where(MetricEvent.id == event_id))
        return result.scalar_one_or_none()
