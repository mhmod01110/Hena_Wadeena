"""Service dependency providers."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from repositories.opportunity_repository import SqlAlchemyInvestmentRepository
from services.dashboard_service import DashboardService
from services.interest_service import InterestService
from services.opportunity_service import OpportunityService


def get_investment_repository(session: AsyncSession = Depends(get_session)) -> SqlAlchemyInvestmentRepository:
    return SqlAlchemyInvestmentRepository(session)


def get_opportunity_service(
    repository: SqlAlchemyInvestmentRepository = Depends(get_investment_repository),
) -> OpportunityService:
    return OpportunityService(repository)


def get_interest_service(
    repository: SqlAlchemyInvestmentRepository = Depends(get_investment_repository),
) -> InterestService:
    return InterestService(repository)


def get_dashboard_service(
    repository: SqlAlchemyInvestmentRepository = Depends(get_investment_repository),
) -> DashboardService:
    return DashboardService(repository)
