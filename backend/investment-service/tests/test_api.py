from __future__ import annotations

import os
import sys

from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from controllers.opportunity_controller import router
from core.dependencies import (
    get_dashboard_service,
    get_interest_service,
    get_investment_repository,
    get_opportunity_service,
)
from schemas.requests import InterestCreate, OpportunityCreate
from services.dashboard_service import DashboardService
from services.interest_service import InterestService
from services.opportunity_service import OpportunityService
from tests.fakes import FakeInvestmentRepository


def build_client() -> tuple[TestClient, FakeInvestmentRepository]:
    repository = FakeInvestmentRepository()
    opportunity_service = OpportunityService(repository)
    interest_service = InterestService(repository)
    dashboard_service = DashboardService(repository)

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_investment_repository] = lambda: repository
    app.dependency_overrides[get_opportunity_service] = lambda: opportunity_service
    app.dependency_overrides[get_interest_service] = lambda: interest_service
    app.dependency_overrides[get_dashboard_service] = lambda: dashboard_service
    return TestClient(app), repository


def seed_open_opportunity(repository: FakeInvestmentRepository):
    service = OpportunityService(repository)
    import asyncio

    return asyncio.run(
        service.create_opportunity(
            owner_id="admin-1",
            role="admin",
            body=OpportunityCreate(
                title="Open Agriculture Deal",
                description="Open agriculture opportunity for export-focused farming.",
                category="agriculture",
                opportunity_type="project",
                location="Kharga",
                min_investment=1500000,
                max_investment=2500000,
                expected_roi="18-22%",
            ),
        )
    )


def test_public_list_returns_open_opportunities_only():
    client, repository = build_client()
    open_opportunity = seed_open_opportunity(repository)

    response = client.get("/api/v1/investments/opportunities")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"][0]["id"] == open_opportunity.id


def test_investor_can_submit_structured_interest():
    client, repository = build_client()
    opportunity = seed_open_opportunity(repository)

    response = client.post(
        f"/api/v1/investments/opportunities/{opportunity.id}/interests",
        headers={"X-User-Id": "investor-1", "X-User-Role": "investor"},
        json={
            "message": "We want to review the detailed financial model.",
            "contact_name": "Investor One",
            "contact_email": "investor1@example.com",
            "contact_phone": "+201000000001",
            "company_name": "Oasis Ventures",
            "investor_type": "Fund",
            "budget_range": "1-5M EGP",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["data"]["contact_name"] == "Investor One"
    assert payload["data"]["status"] == "submitted"


def test_owner_can_list_interests_for_their_opportunity():
    client, repository = build_client()
    opportunity = seed_open_opportunity(repository)
    interest_service = InterestService(repository)
    import asyncio

    asyncio.run(
        interest_service.express_interest(
            investor_id="investor-1",
            opportunity=opportunity,
            body=InterestCreate(
                message="Interested in joining the deal.",
                contact_name="Investor One",
                contact_email="investor1@example.com",
                contact_phone="+201000000001",
            ),
        )
    )

    response = client.get(
        f"/api/v1/investments/opportunities/{opportunity.id}/interests",
        headers={"X-User-Id": "admin-1", "X-User-Role": "admin"},
    )

    assert response.status_code == 200
    assert response.json()["meta"]["total"] == 1


def test_verify_endpoint_requires_review_role():
    client, repository = build_client()
    opportunity = seed_open_opportunity(repository)
    repository.opportunities[opportunity.id].status = "pending_review"
    repository.opportunities[opportunity.id].is_verified = False

    forbidden = client.patch(
        f"/api/v1/investments/opportunities/{opportunity.id}/verify",
        headers={"X-User-Id": "investor-1", "X-User-Role": "investor"},
    )
    allowed = client.patch(
        f"/api/v1/investments/opportunities/{opportunity.id}/verify",
        headers={"X-User-Id": "reviewer-1", "X-User-Role": "reviewer"},
    )

    assert forbidden.status_code == 403
    assert allowed.status_code == 200
    assert allowed.json()["data"]["status"] == "open"
