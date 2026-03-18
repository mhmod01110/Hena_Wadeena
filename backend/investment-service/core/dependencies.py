"""Service dependency providers."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from repositories.opportunity_repository import SqlAlchemyOpportunityRepository
from services.opportunity_service import OpportunityService


def get_opportunity_service(
    session: AsyncSession = Depends(get_session),
) -> OpportunityService:
    repository = SqlAlchemyOpportunityRepository(session)
    return OpportunityService(repository)
