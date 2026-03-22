"""Business logic for investment interests and watchlists."""

from __future__ import annotations

from typing import Optional

from interfaces.opportunity_repository import IInvestmentRepository
from models import InvestmentInterest, InvestmentOpportunity, InvestmentWatchlist
from schemas.requests import InterestCreate, InterestStatusUpdateRequest


ALLOWED_INTEREST_STATUSES = {"submitted", "under_review", "accepted", "rejected", "withdrawn"}


class InterestService:

    def __init__(self, repository: IInvestmentRepository):
        self._repository = repository

    async def express_interest(
        self,
        *,
        investor_id: str,
        opportunity: InvestmentOpportunity,
        body: InterestCreate,
    ) -> InvestmentInterest:
        if opportunity.status != "open":
            raise ValueError("Only open opportunities can receive investment interest")

        existing = await self._repository.get_interest_by_opportunity_and_investor(opportunity.id, investor_id)
        if existing:
            raise ValueError("You already submitted interest for this opportunity")

        entity = InvestmentInterest(
            opportunity_id=opportunity.id,
            investor_id=investor_id,
            message=body.message.strip(),
            contact_name=body.contact_name.strip(),
            contact_email=body.contact_email.strip(),
            contact_phone=body.contact_phone.strip(),
            company_name=body.company_name.strip() if body.company_name else None,
            investor_type=body.investor_type.strip() if body.investor_type else None,
            budget_range=body.budget_range.strip() if body.budget_range else None,
            status="submitted",
        )
        created = await self._repository.create_interest(entity)
        await self._repository.sync_interest_count(opportunity.id)
        return created

    async def list_my_interests(
        self,
        investor_id: str,
        *,
        status_filter: Optional[str] = None,
    ) -> list[InvestmentInterest]:
        return await self._repository.list_interests_for_investor(investor_id, status_filter=status_filter)

    async def list_opportunity_interests(
        self,
        opportunity_id: str,
        *,
        status_filter: Optional[str] = None,
    ) -> list[InvestmentInterest]:
        return await self._repository.list_interests_for_opportunity(opportunity_id, status_filter=status_filter)

    async def get_interest(self, interest_id: str) -> Optional[InvestmentInterest]:
        return await self._repository.get_interest_by_id(interest_id)

    async def update_interest_status(
        self,
        *,
        entity: InvestmentInterest,
        body: InterestStatusUpdateRequest,
    ) -> InvestmentInterest:
        if body.status not in ALLOWED_INTEREST_STATUSES:
            raise ValueError("Unsupported interest status")

        entity.status = body.status
        entity.owner_notes = body.owner_notes.strip() if body.owner_notes else None
        updated = await self._repository.update_interest(entity)
        await self._repository.sync_interest_count(entity.opportunity_id)
        return updated

    async def add_watchlist(self, investor_id: str, opportunity_id: str) -> InvestmentWatchlist:
        existing = await self._repository.get_watchlist_entry(investor_id, opportunity_id)
        if existing:
            return existing

        return await self._repository.add_watchlist(
            InvestmentWatchlist(investor_id=investor_id, opportunity_id=opportunity_id)
        )

    async def remove_watchlist(self, investor_id: str, opportunity_id: str) -> None:
        existing = await self._repository.get_watchlist_entry(investor_id, opportunity_id)
        if existing:
            await self._repository.remove_watchlist(existing)
