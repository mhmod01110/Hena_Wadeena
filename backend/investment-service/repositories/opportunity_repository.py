"""SQLAlchemy repository for the investment domain."""

from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from interfaces.opportunity_repository import IInvestmentRepository
from models import InvestmentInterest, InvestmentOpportunity, InvestmentWatchlist


class SqlAlchemyInvestmentRepository(IInvestmentRepository):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_opportunity(self, entity: InvestmentOpportunity) -> InvestmentOpportunity:
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def list_opportunities(
        self,
        *,
        category: Optional[str] = None,
        opportunity_type: Optional[str] = None,
        location: Optional[str] = None,
        owner_id: Optional[str] = None,
        status_filter: Optional[str] = None,
    ) -> list[InvestmentOpportunity]:
        query = select(InvestmentOpportunity)
        if category:
            query = query.where(InvestmentOpportunity.category == category)
        if opportunity_type:
            query = query.where(InvestmentOpportunity.opportunity_type == opportunity_type)
        if owner_id:
            query = query.where(InvestmentOpportunity.owner_id == owner_id)
        if status_filter:
            query = query.where(InvestmentOpportunity.status == status_filter)
        if location:
            query = query.where(InvestmentOpportunity.location.ilike(f"%{location}%"))

        query = query.order_by(InvestmentOpportunity.created_at.desc())
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_opportunity_by_id(self, opportunity_id: str) -> Optional[InvestmentOpportunity]:
        result = await self._session.execute(
            select(InvestmentOpportunity).where(InvestmentOpportunity.id == opportunity_id)
        )
        return result.scalar_one_or_none()

    async def get_opportunities_by_ids(self, opportunity_ids: list[str]) -> list[InvestmentOpportunity]:
        if not opportunity_ids:
            return []

        result = await self._session.execute(
            select(InvestmentOpportunity).where(InvestmentOpportunity.id.in_(opportunity_ids))
        )
        return list(result.scalars().all())

    async def update_opportunity(self, entity: InvestmentOpportunity) -> InvestmentOpportunity:
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def create_interest(self, entity: InvestmentInterest) -> InvestmentInterest:
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def get_interest_by_id(self, interest_id: str) -> Optional[InvestmentInterest]:
        result = await self._session.execute(
            select(InvestmentInterest).where(InvestmentInterest.id == interest_id)
        )
        return result.scalar_one_or_none()

    async def get_interest_by_opportunity_and_investor(
        self,
        opportunity_id: str,
        investor_id: str,
    ) -> Optional[InvestmentInterest]:
        result = await self._session.execute(
            select(InvestmentInterest).where(
                InvestmentInterest.opportunity_id == opportunity_id,
                InvestmentInterest.investor_id == investor_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_interests_for_investor(
        self,
        investor_id: str,
        *,
        status_filter: Optional[str] = None,
    ) -> list[InvestmentInterest]:
        query = select(InvestmentInterest).where(InvestmentInterest.investor_id == investor_id)
        if status_filter:
            query = query.where(InvestmentInterest.status == status_filter)
        query = query.order_by(InvestmentInterest.created_at.desc())
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def list_interests_for_opportunity(
        self,
        opportunity_id: str,
        *,
        status_filter: Optional[str] = None,
    ) -> list[InvestmentInterest]:
        query = select(InvestmentInterest).where(InvestmentInterest.opportunity_id == opportunity_id)
        if status_filter:
            query = query.where(InvestmentInterest.status == status_filter)
        query = query.order_by(InvestmentInterest.created_at.desc())
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def update_interest(self, entity: InvestmentInterest) -> InvestmentInterest:
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def sync_interest_count(self, opportunity_id: str) -> int:
        count_result = await self._session.execute(
            select(func.count(InvestmentInterest.id)).where(
                InvestmentInterest.opportunity_id == opportunity_id,
                InvestmentInterest.status != "withdrawn",
            )
        )
        count = int(count_result.scalar() or 0)

        opportunity = await self.get_opportunity_by_id(opportunity_id)
        if opportunity:
            opportunity.interest_count = count
            await self._session.flush()
        return count

    async def get_watchlist_entry(
        self,
        investor_id: str,
        opportunity_id: str,
    ) -> Optional[InvestmentWatchlist]:
        result = await self._session.execute(
            select(InvestmentWatchlist).where(
                InvestmentWatchlist.investor_id == investor_id,
                InvestmentWatchlist.opportunity_id == opportunity_id,
            )
        )
        return result.scalar_one_or_none()

    async def add_watchlist(self, entity: InvestmentWatchlist) -> InvestmentWatchlist:
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def remove_watchlist(self, entity: InvestmentWatchlist) -> None:
        await self._session.delete(entity)
        await self._session.flush()

    async def list_watchlist_for_investor(self, investor_id: str) -> list[InvestmentWatchlist]:
        result = await self._session.execute(
            select(InvestmentWatchlist)
            .where(InvestmentWatchlist.investor_id == investor_id)
            .order_by(InvestmentWatchlist.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_watchlisted_opportunity_ids(self, investor_id: str, opportunity_ids: list[str]) -> set[str]:
        if not opportunity_ids:
            return set()

        result = await self._session.execute(
            select(InvestmentWatchlist.opportunity_id).where(
                InvestmentWatchlist.investor_id == investor_id,
                InvestmentWatchlist.opportunity_id.in_(opportunity_ids),
            )
        )
        return {row[0] for row in result.all()}
