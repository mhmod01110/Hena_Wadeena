"""Business logic for the investor dashboard."""

from __future__ import annotations

from interfaces.opportunity_repository import IInvestmentRepository


class DashboardService:

    def __init__(self, repository: IInvestmentRepository):
        self._repository = repository

    async def build_dashboard(self, investor_id: str) -> dict:
        interests = await self._repository.list_interests_for_investor(investor_id)
        watchlist_entries = await self._repository.list_watchlist_for_investor(investor_id)
        watchlist_ids = [item.opportunity_id for item in watchlist_entries]

        watched_opportunities = await self._repository.get_opportunities_by_ids(watchlist_ids)
        watched_by_id = {item.id: item for item in watched_opportunities}
        ordered_watchlist = [watched_by_id[item_id] for item_id in watchlist_ids if item_id in watched_by_id]

        interest_opportunity_ids = [item.opportunity_id for item in interests]
        related_opportunities = await self._repository.get_opportunities_by_ids(
            list({*watchlist_ids, *interest_opportunity_ids})
        )
        related_by_id = {item.id: item for item in related_opportunities}

        status_counts: dict[str, int] = {}
        categories = set()
        for interest in interests:
            status_counts[interest.status] = status_counts.get(interest.status, 0) + 1
            opportunity = related_by_id.get(interest.opportunity_id)
            if opportunity:
                categories.add(opportunity.category)

        for opportunity in ordered_watchlist:
            categories.add(opportunity.category)

        excluded_ids = list({*watchlist_ids, *interest_opportunity_ids})
        recommended: list = []
        for category in sorted(categories):
            matches = await self._repository.list_opportunities(category=category, status_filter="open")
            for opportunity in matches:
                if opportunity.id in excluded_ids:
                    continue
                recommended.append(opportunity)
                if len(recommended) >= 4:
                    break
            if len(recommended) >= 4:
                break

        if len(recommended) < 4:
            latest = await self._repository.list_opportunities(status_filter="open")
            for opportunity in latest:
                if opportunity.id in excluded_ids or any(item.id == opportunity.id for item in recommended):
                    continue
                recommended.append(opportunity)
                if len(recommended) >= 4:
                    break

        return {
            "status_counts": status_counts,
            "recent_interests": interests[:5],
            "watchlist": ordered_watchlist,
            "recommended": recommended[:4],
        }
