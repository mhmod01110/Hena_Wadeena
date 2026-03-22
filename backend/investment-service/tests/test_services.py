from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from schemas.requests import InterestCreate, InterestStatusUpdateRequest, OpportunityCreate
from services.dashboard_service import DashboardService
from services.interest_service import InterestService
from services.opportunity_service import OpportunityService
from tests.fakes import FakeInvestmentRepository


@pytest.mark.asyncio
async def test_create_opportunity_defaults_to_pending_review_for_investor():
    repository = FakeInvestmentRepository()
    service = OpportunityService(repository)

    opportunity = await service.create_opportunity(
        owner_id="investor-1",
        role="investor",
        body=OpportunityCreate(
            title="Date Processing Plant",
            description="A clean processing facility for New Valley date exports.",
            category="manufacturing",
            opportunity_type="project",
            location="Kharga",
            min_investment=1000000,
            max_investment=2000000,
            expected_roi="15-20%",
        ),
    )

    assert opportunity.status == "pending_review"
    assert opportunity.is_verified is False


@pytest.mark.asyncio
async def test_duplicate_interest_is_rejected_and_interest_count_is_synced():
    repository = FakeInvestmentRepository()
    opportunity_service = OpportunityService(repository)
    interest_service = InterestService(repository)

    opportunity = await opportunity_service.create_opportunity(
        owner_id="admin-1",
        role="admin",
        body=OpportunityCreate(
            title="Solar Startup",
            description="A startup for modular irrigation hardware.",
            category="renewable_energy",
            opportunity_type="startup",
            location="Dakhla",
            min_investment=250000,
            max_investment=900000,
            expected_roi="14-18%",
        ),
    )

    interest_body = InterestCreate(
        message="I want to participate in the seed round.",
        contact_name="Investor One",
        contact_email="investor1@example.com",
        contact_phone="+201000000001",
        company_name="Oasis Ventures",
        investor_type="Fund",
        budget_range="1-5M EGP",
    )
    await interest_service.express_interest(investor_id="investor-1", opportunity=opportunity, body=interest_body)

    with pytest.raises(ValueError, match="already submitted"):
        await interest_service.express_interest(investor_id="investor-1", opportunity=opportunity, body=interest_body)

    assert repository.opportunities[opportunity.id].interest_count == 1


@pytest.mark.asyncio
async def test_interest_status_update_keeps_interest_count_in_sync():
    repository = FakeInvestmentRepository()
    opportunity_service = OpportunityService(repository)
    interest_service = InterestService(repository)

    opportunity = await opportunity_service.create_opportunity(
        owner_id="admin-1",
        role="admin",
        body=OpportunityCreate(
            title="Tourism Lodge",
            description="An eco retreat beside the White Desert.",
            category="tourism",
            opportunity_type="project",
            location="Farafra",
            min_investment=1500000,
            max_investment=2500000,
            expected_roi="18-22%",
        ),
    )
    interest = await interest_service.express_interest(
        investor_id="investor-1",
        opportunity=opportunity,
        body=InterestCreate(
            message="We would like to schedule a diligence call.",
            contact_name="Investor One",
            contact_email="investor1@example.com",
            contact_phone="+201000000001",
        ),
    )

    updated = await interest_service.update_interest_status(
        entity=interest,
        body=InterestStatusUpdateRequest(status="withdrawn", owner_notes="Investor withdrew"),
    )

    assert updated.status == "withdrawn"
    assert repository.opportunities[opportunity.id].interest_count == 0


@pytest.mark.asyncio
async def test_dashboard_aggregates_interests_watchlist_and_recommendations():
    repository = FakeInvestmentRepository()
    opportunity_service = OpportunityService(repository)
    interest_service = InterestService(repository)
    dashboard_service = DashboardService(repository)

    agriculture = await opportunity_service.create_opportunity(
        owner_id="admin-1",
        role="admin",
        body=OpportunityCreate(
            title="Integrated Farm",
            description="Large-scale farm with packing and irrigation.",
            category="agriculture",
            opportunity_type="project",
            location="Kharga",
            min_investment=2000000,
            max_investment=4000000,
            expected_roi="17-20%",
        ),
    )
    tourism = await opportunity_service.create_opportunity(
        owner_id="admin-1",
        role="admin",
        body=OpportunityCreate(
            title="Desert Lodge",
            description="A boutique eco-lodge near desert attractions.",
            category="tourism",
            opportunity_type="project",
            location="Farafra",
            min_investment=2500000,
            max_investment=3500000,
            expected_roi="18-24%",
        ),
    )
    recommendation = await opportunity_service.create_opportunity(
        owner_id="admin-1",
        role="admin",
        body=OpportunityCreate(
            title="Date Export Hub",
            description="An export-focused packing hub for local growers.",
            category="agriculture",
            opportunity_type="partnership",
            location="Dakhla",
            min_investment=1800000,
            max_investment=3200000,
            expected_roi="16-21%",
        ),
    )

    await interest_service.express_interest(
        investor_id="investor-1",
        opportunity=agriculture,
        body=InterestCreate(
            message="Please share the financial model.",
            contact_name="Investor One",
            contact_email="investor1@example.com",
            contact_phone="+201000000001",
        ),
    )
    await interest_service.add_watchlist("investor-1", tourism.id)

    dashboard = await dashboard_service.build_dashboard("investor-1")

    assert dashboard["status_counts"]["submitted"] == 1
    assert len(dashboard["watchlist"]) == 1
    assert dashboard["watchlist"][0].id == tourism.id
    assert recommendation.id in [item.id for item in dashboard["recommended"]]
