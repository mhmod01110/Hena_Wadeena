"""Service dependency providers."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from repositories.metric_event_repository import SqlAlchemyMetricEventRepository
from services.metric_event_service import MetricEventService


def get_metric_event_service(
    session: AsyncSession = Depends(get_session),
) -> MetricEventService:
    repository = SqlAlchemyMetricEventRepository(session)
    return MetricEventService(repository)
