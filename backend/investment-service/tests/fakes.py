"""Test doubles for investment-service tests."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from interfaces.opportunity_repository import IInvestmentRepository
from models import InvestmentInterest, InvestmentOpportunity, InvestmentWatchlist


def _now() -> datetime:
    return datetime.now(timezone.utc)


class FakeInvestmentRepository(IInvestmentRepository):
    def __init__(self):
        self.opportunities: dict[str, InvestmentOpportunity] = {}
        self.interests: dict[str, InvestmentInterest] = {}
        self.watchlist_entries: dict[tuple[str, str], InvestmentWatchlist] = {}

    @staticmethod
    def _ensure_base_fields(entity) -> None:
        if not getattr(entity, "id", None):
            entity.id = str(uuid.uuid4())
        if not getattr(entity, "created_at", None):
            entity.created_at = _now()
        entity.updated_at = _now()

    async def create_opportunity(self, entity: InvestmentOpportunity) -> InvestmentOpportunity:
        self._ensure_base_fields(entity)
        self.opportunities[entity.id] = entity
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
        items = list(self.opportunities.values())
        if category:
            items = [item for item in items if item.category == category]
        if opportunity_type:
            items = [item for item in items if item.opportunity_type == opportunity_type]
        if owner_id:
            items = [item for item in items if item.owner_id == owner_id]
        if status_filter:
            items = [item for item in items if item.status == status_filter]
        if location:
            items = [item for item in items if location.lower() in item.location.lower()]
        return sorted(items, key=lambda item: item.created_at, reverse=True)

    async def get_opportunity_by_id(self, opportunity_id: str) -> Optional[InvestmentOpportunity]:
        return self.opportunities.get(opportunity_id)

    async def get_opportunities_by_ids(self, opportunity_ids: list[str]) -> list[InvestmentOpportunity]:
        return [self.opportunities[opportunity_id] for opportunity_id in opportunity_ids if opportunity_id in self.opportunities]

    async def update_opportunity(self, entity: InvestmentOpportunity) -> InvestmentOpportunity:
        entity.updated_at = _now()
        self.opportunities[entity.id] = entity
        return entity

    async def create_interest(self, entity: InvestmentInterest) -> InvestmentInterest:
        self._ensure_base_fields(entity)
        self.interests[entity.id] = entity
        return entity

    async def get_interest_by_id(self, interest_id: str) -> Optional[InvestmentInterest]:
        return self.interests.get(interest_id)

    async def get_interest_by_opportunity_and_investor(
        self,
        opportunity_id: str,
        investor_id: str,
    ) -> Optional[InvestmentInterest]:
        for interest in self.interests.values():
            if interest.opportunity_id == opportunity_id and interest.investor_id == investor_id:
                return interest
        return None

    async def list_interests_for_investor(
        self,
        investor_id: str,
        *,
        status_filter: Optional[str] = None,
    ) -> list[InvestmentInterest]:
        items = [interest for interest in self.interests.values() if interest.investor_id == investor_id]
        if status_filter:
            items = [interest for interest in items if interest.status == status_filter]
        return sorted(items, key=lambda item: item.created_at, reverse=True)

    async def list_interests_for_opportunity(
        self,
        opportunity_id: str,
        *,
        status_filter: Optional[str] = None,
    ) -> list[InvestmentInterest]:
        items = [interest for interest in self.interests.values() if interest.opportunity_id == opportunity_id]
        if status_filter:
            items = [interest for interest in items if interest.status == status_filter]
        return sorted(items, key=lambda item: item.created_at, reverse=True)

    async def update_interest(self, entity: InvestmentInterest) -> InvestmentInterest:
        entity.updated_at = _now()
        self.interests[entity.id] = entity
        return entity

    async def sync_interest_count(self, opportunity_id: str) -> int:
        count = sum(
            1
            for interest in self.interests.values()
            if interest.opportunity_id == opportunity_id and interest.status != "withdrawn"
        )
        if opportunity_id in self.opportunities:
            self.opportunities[opportunity_id].interest_count = count
            self.opportunities[opportunity_id].updated_at = _now()
        return count

    async def get_watchlist_entry(
        self,
        investor_id: str,
        opportunity_id: str,
    ) -> Optional[InvestmentWatchlist]:
        return self.watchlist_entries.get((investor_id, opportunity_id))

    async def add_watchlist(self, entity: InvestmentWatchlist) -> InvestmentWatchlist:
        self._ensure_base_fields(entity)
        self.watchlist_entries[(entity.investor_id, entity.opportunity_id)] = entity
        return entity

    async def remove_watchlist(self, entity: InvestmentWatchlist) -> None:
        self.watchlist_entries.pop((entity.investor_id, entity.opportunity_id), None)

    async def list_watchlist_for_investor(self, investor_id: str) -> list[InvestmentWatchlist]:
        items = [entry for entry in self.watchlist_entries.values() if entry.investor_id == investor_id]
        return sorted(items, key=lambda item: item.created_at, reverse=True)

    async def get_watchlisted_opportunity_ids(self, investor_id: str, opportunity_ids: list[str]) -> set[str]:
        return {
            opportunity_id
            for opportunity_id in opportunity_ids
            if (investor_id, opportunity_id) in self.watchlist_entries
        }
