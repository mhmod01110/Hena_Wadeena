"""Business logic for investment opportunities."""

from __future__ import annotations

from typing import Optional

from interfaces.opportunity_repository import IInvestmentRepository
from models import InvestmentOpportunity
from schemas.requests import OpportunityCreate, OpportunityUpdate


ALLOWED_OPPORTUNITY_TYPES = {"project", "startup", "land", "partnership", "franchise"}
ALLOWED_OPPORTUNITY_STATUSES = {"pending_review", "open", "funded", "closed"}
REVIEW_ROLES = {"reviewer", "admin", "super_admin"}


class OpportunityService:

    def __init__(self, repository: IInvestmentRepository):
        self._repository = repository

    @staticmethod
    def _validate_investment_range(min_investment: float, max_investment: float) -> None:
        if min_investment > max_investment:
            raise ValueError("Minimum investment cannot be greater than maximum investment")

    @staticmethod
    def _validate_opportunity_type(opportunity_type: str) -> None:
        if opportunity_type not in ALLOWED_OPPORTUNITY_TYPES:
            raise ValueError("Unsupported opportunity type")

    async def create_opportunity(
        self,
        *,
        owner_id: str,
        role: str,
        body: OpportunityCreate,
    ) -> InvestmentOpportunity:
        self._validate_investment_range(body.min_investment, body.max_investment)
        self._validate_opportunity_type(body.opportunity_type)

        status = "open" if role in REVIEW_ROLES else "pending_review"
        is_verified = role in REVIEW_ROLES
        entity = InvestmentOpportunity(
            owner_id=owner_id,
            title=body.title.strip(),
            description=body.description.strip(),
            category=body.category.strip(),
            opportunity_type=body.opportunity_type,
            location=body.location.strip(),
            min_investment=float(body.min_investment),
            max_investment=float(body.max_investment),
            expected_roi=body.expected_roi.strip(),
            status=status,
            is_verified=is_verified,
            interest_count=0,
        )
        return await self._repository.create_opportunity(entity)

    async def list_opportunities(
        self,
        *,
        category: Optional[str] = None,
        opportunity_type: Optional[str] = None,
        location: Optional[str] = None,
        owner_id: Optional[str] = None,
        status_filter: Optional[str] = None,
    ) -> list[InvestmentOpportunity]:
        if opportunity_type:
            self._validate_opportunity_type(opportunity_type)

        return await self._repository.list_opportunities(
            category=category,
            opportunity_type=opportunity_type,
            location=location,
            owner_id=owner_id,
            status_filter=status_filter,
        )

    async def get_opportunity(self, opportunity_id: str) -> Optional[InvestmentOpportunity]:
        return await self._repository.get_opportunity_by_id(opportunity_id)

    async def update_opportunity(
        self,
        *,
        entity: InvestmentOpportunity,
        body: OpportunityUpdate,
        can_review: bool,
    ) -> InvestmentOpportunity:
        payload = body.model_dump(exclude_unset=True)
        min_investment = float(payload.get("min_investment", entity.min_investment))
        max_investment = float(payload.get("max_investment", entity.max_investment))
        self._validate_investment_range(min_investment, max_investment)

        if "opportunity_type" in payload:
            self._validate_opportunity_type(str(payload["opportunity_type"]))

        for field in (
            "title",
            "description",
            "category",
            "opportunity_type",
            "location",
            "min_investment",
            "max_investment",
            "expected_roi",
        ):
            if field not in payload:
                continue
            value = payload[field]
            if isinstance(value, str):
                value = value.strip()
            setattr(entity, field, value)

        if can_review and "status" in payload and payload["status"] in ALLOWED_OPPORTUNITY_STATUSES:
            entity.status = str(payload["status"])
            entity.is_verified = entity.status == "open"

        return await self._repository.update_opportunity(entity)

    async def verify_opportunity(self, entity: InvestmentOpportunity) -> InvestmentOpportunity:
        entity.is_verified = True
        entity.status = "open"
        return await self._repository.update_opportunity(entity)
