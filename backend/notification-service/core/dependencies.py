"""Service dependency providers."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from repositories.notification_message_repository import SqlAlchemyNotificationMessageRepository
from services.notification_message_service import NotificationMessageService


def get_notification_message_service(
    session: AsyncSession = Depends(get_session),
) -> NotificationMessageService:
    repository = SqlAlchemyNotificationMessageRepository(session)
    return NotificationMessageService(repository)
