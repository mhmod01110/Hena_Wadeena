"""Service dependency providers."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from repositories.admin_repository import SqlAlchemyAdminRepository
from services.admin_service import AdminService


def get_admin_service(
    session: AsyncSession = Depends(get_session),
) -> AdminService:
    repository = SqlAlchemyAdminRepository(session)
    return AdminService(repository)
