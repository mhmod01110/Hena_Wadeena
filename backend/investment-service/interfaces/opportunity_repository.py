"""Repository contract for the investment domain."""

from abc import ABC, abstractmethod
from typing import Optional

from models import InvestmentInterest, InvestmentOpportunity, InvestmentWatchlist


class IInvestmentRepository(ABC):

    @abstractmethod
    async def create_opportunity(self, entity: InvestmentOpportunity) -> InvestmentOpportunity:
        raise NotImplementedError

    @abstractmethod
    async def list_opportunities(
        self,
        *,
        category: Optional[str] = None,
        opportunity_type: Optional[str] = None,
        location: Optional[str] = None,
        owner_id: Optional[str] = None,
        status_filter: Optional[str] = None,
    ) -> list[InvestmentOpportunity]:
        raise NotImplementedError

    @abstractmethod
    async def get_opportunity_by_id(self, opportunity_id: str) -> Optional[InvestmentOpportunity]:
        raise NotImplementedError

    @abstractmethod
    async def get_opportunities_by_ids(self, opportunity_ids: list[str]) -> list[InvestmentOpportunity]:
        raise NotImplementedError

    @abstractmethod
    async def update_opportunity(self, entity: InvestmentOpportunity) -> InvestmentOpportunity:
        raise NotImplementedError

    @abstractmethod
    async def create_interest(self, entity: InvestmentInterest) -> InvestmentInterest:
        raise NotImplementedError

    @abstractmethod
    async def get_interest_by_id(self, interest_id: str) -> Optional[InvestmentInterest]:
        raise NotImplementedError

    @abstractmethod
    async def get_interest_by_opportunity_and_investor(
        self,
        opportunity_id: str,
        investor_id: str,
    ) -> Optional[InvestmentInterest]:
        raise NotImplementedError

    @abstractmethod
    async def list_interests_for_investor(
        self,
        investor_id: str,
        *,
        status_filter: Optional[str] = None,
    ) -> list[InvestmentInterest]:
        raise NotImplementedError

    @abstractmethod
    async def list_interests_for_opportunity(
        self,
        opportunity_id: str,
        *,
        status_filter: Optional[str] = None,
    ) -> list[InvestmentInterest]:
        raise NotImplementedError

    @abstractmethod
    async def update_interest(self, entity: InvestmentInterest) -> InvestmentInterest:
        raise NotImplementedError

    @abstractmethod
    async def sync_interest_count(self, opportunity_id: str) -> int:
        raise NotImplementedError

    @abstractmethod
    async def get_watchlist_entry(
        self,
        investor_id: str,
        opportunity_id: str,
    ) -> Optional[InvestmentWatchlist]:
        raise NotImplementedError

    @abstractmethod
    async def add_watchlist(self, entity: InvestmentWatchlist) -> InvestmentWatchlist:
        raise NotImplementedError

    @abstractmethod
    async def remove_watchlist(self, entity: InvestmentWatchlist) -> None:
        raise NotImplementedError

    @abstractmethod
    async def list_watchlist_for_investor(self, investor_id: str) -> list[InvestmentWatchlist]:
        raise NotImplementedError

    @abstractmethod
    async def get_watchlisted_opportunity_ids(self, investor_id: str, opportunity_ids: list[str]) -> set[str]:
        raise NotImplementedError
