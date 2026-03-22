"""HTTP controller for investment opportunities, interests, watchlists, and dashboard."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from core.dependencies import (
    get_dashboard_service,
    get_interest_service,
    get_investment_repository,
    get_opportunity_service,
)
from repositories.opportunity_repository import SqlAlchemyInvestmentRepository
from schemas.requests import (
    InterestCreate,
    InterestStatusUpdateRequest,
    OpportunityCreate,
    OpportunityUpdate,
)
from schemas.responses import InterestResponse, InvestorDashboardResponse, OpportunityResponse
from services.dashboard_service import DashboardService
from services.interest_service import InterestService
from services.opportunity_service import OpportunityService


router = APIRouter()


CREATOR_ROLES = {"investor", "merchant", "admin", "super_admin"}
INVESTOR_ROLES = {"investor"}
REVIEW_ROLES = {"reviewer", "admin", "super_admin"}


def _envelope(data: Any = None, meta: Optional[dict] = None, error: Optional[str] = None, success: bool = True) -> dict:
    return {"success": success, "data": data, "meta": meta, "error": error}


def _role(request: Request) -> str:
    return request.headers.get("X-User-Role", "tourist")


def _optional_user_id(request: Request) -> Optional[str]:
    return request.headers.get("X-User-Id")


def _require_user_id(request: Request) -> str:
    uid = _optional_user_id(request)
    if not uid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")
    return uid


def _ensure_role(request: Request, allowed_roles: set[str]) -> str:
    role = _role(request)
    if role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role not allowed for this action")
    return role


def _can_review(request: Request) -> bool:
    return _role(request) in REVIEW_ROLES


def _can_view_opportunity(request: Request, owner_id: str, opportunity_status: str) -> bool:
    user_id = _optional_user_id(request)
    role = _role(request)
    return opportunity_status == "open" or role in REVIEW_ROLES or owner_id == user_id


def _investment_range(min_investment: float, max_investment: float) -> str:
    return f"{float(min_investment):,.0f} - {float(max_investment):,.0f} EGP"


def _to_opportunity_response(entity, is_watchlisted: bool = False) -> OpportunityResponse:
    return OpportunityResponse(
        id=str(entity.id),
        owner_id=entity.owner_id,
        title=entity.title,
        category=entity.category,
        opportunity_type=entity.opportunity_type,
        location=entity.location,
        min_investment=float(entity.min_investment),
        max_investment=float(entity.max_investment),
        investment_range=_investment_range(entity.min_investment, entity.max_investment),
        expected_roi=entity.expected_roi,
        description=entity.description,
        status=entity.status,
        is_verified=bool(entity.is_verified),
        interest_count=int(entity.interest_count or 0),
        is_watchlisted=is_watchlisted,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def _to_interest_response(entity, opportunity=None) -> InterestResponse:
    return InterestResponse(
        id=str(entity.id),
        opportunity_id=entity.opportunity_id,
        opportunity_title=getattr(opportunity, "title", None),
        opportunity_category=getattr(opportunity, "category", None),
        opportunity_location=getattr(opportunity, "location", None),
        opportunity_type=getattr(opportunity, "opportunity_type", None),
        investor_id=entity.investor_id,
        message=entity.message,
        contact_name=entity.contact_name,
        contact_email=entity.contact_email,
        contact_phone=entity.contact_phone,
        company_name=entity.company_name,
        investor_type=entity.investor_type,
        budget_range=entity.budget_range,
        status=entity.status,
        owner_notes=entity.owner_notes,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


async def _watchlisted_ids_for_request(
    request: Request,
    repository: SqlAlchemyInvestmentRepository,
    opportunity_ids: list[str],
) -> set[str]:
    user_id = _optional_user_id(request)
    if not user_id or _role(request) not in INVESTOR_ROLES:
        return set()
    return await repository.get_watchlisted_opportunity_ids(user_id, opportunity_ids)


@router.post("/api/v1/investments/opportunities", status_code=status.HTTP_201_CREATED)
async def create_opportunity(
    body: OpportunityCreate,
    request: Request,
    service: OpportunityService = Depends(get_opportunity_service),
):
    role = _ensure_role(request, CREATOR_ROLES)
    entity = await service.create_opportunity(owner_id=_require_user_id(request), role=role, body=body)
    return _envelope(_to_opportunity_response(entity).model_dump())


@router.get("/api/v1/investments/opportunities")
async def list_opportunities(
    request: Request,
    category: Optional[str] = Query(default=None),
    opportunity_type: Optional[str] = Query(default=None),
    location: Optional[str] = Query(default=None),
    owner_id: Optional[str] = Query(default=None),
    status_filter: Optional[str] = Query(default=None, alias="status"),
    service: OpportunityService = Depends(get_opportunity_service),
    repository: SqlAlchemyInvestmentRepository = Depends(get_investment_repository),
):
    requester_id = _optional_user_id(request)
    if owner_id and owner_id != requester_id and not _can_review(request):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to view other owners' drafts")

    effective_status = status_filter if (_can_review(request) or owner_id == requester_id) else "open"
    entities = await service.list_opportunities(
        category=category,
        opportunity_type=opportunity_type,
        location=location,
        owner_id=owner_id,
        status_filter=effective_status,
    )
    visible_entities = [entity for entity in entities if _can_view_opportunity(request, entity.owner_id, entity.status)]
    watchlisted_ids = await _watchlisted_ids_for_request(
        request,
        repository,
        [entity.id for entity in visible_entities],
    )
    items = [
        _to_opportunity_response(entity, is_watchlisted=entity.id in watchlisted_ids).model_dump()
        for entity in visible_entities
    ]
    return _envelope(items, meta={"total": len(items)})


@router.get("/api/v1/investments/opportunities/{opportunity_id}")
async def get_opportunity(
    opportunity_id: str,
    request: Request,
    service: OpportunityService = Depends(get_opportunity_service),
    repository: SqlAlchemyInvestmentRepository = Depends(get_investment_repository),
):
    entity = await service.get_opportunity(opportunity_id)
    if not entity or not _can_view_opportunity(request, entity.owner_id, entity.status):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    watchlisted_ids = await _watchlisted_ids_for_request(request, repository, [entity.id])
    return _envelope(_to_opportunity_response(entity, entity.id in watchlisted_ids).model_dump())


@router.patch("/api/v1/investments/opportunities/{opportunity_id}")
async def update_opportunity(
    opportunity_id: str,
    body: OpportunityUpdate,
    request: Request,
    service: OpportunityService = Depends(get_opportunity_service),
):
    entity = await service.get_opportunity(opportunity_id)
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    user_id = _require_user_id(request)
    can_review = _can_review(request)
    if not can_review and entity.owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to update this opportunity")

    updated = await service.update_opportunity(entity=entity, body=body, can_review=can_review)
    return _envelope(_to_opportunity_response(updated).model_dump())


@router.patch("/api/v1/investments/opportunities/{opportunity_id}/verify")
async def verify_opportunity(
    opportunity_id: str,
    request: Request,
    service: OpportunityService = Depends(get_opportunity_service),
):
    _ensure_role(request, REVIEW_ROLES)
    entity = await service.get_opportunity(opportunity_id)
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    verified = await service.verify_opportunity(entity)
    return _envelope(_to_opportunity_response(verified).model_dump())


@router.post("/api/v1/investments/opportunities/{opportunity_id}/interests", status_code=status.HTTP_201_CREATED)
async def express_interest(
    opportunity_id: str,
    body: InterestCreate,
    request: Request,
    opportunity_service: OpportunityService = Depends(get_opportunity_service),
    interest_service: InterestService = Depends(get_interest_service),
):
    _ensure_role(request, INVESTOR_ROLES)
    opportunity = await opportunity_service.get_opportunity(opportunity_id)
    if not opportunity or not _can_view_opportunity(request, opportunity.owner_id, opportunity.status):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    try:
        entity = await interest_service.express_interest(
            investor_id=_require_user_id(request),
            opportunity=opportunity,
            body=body,
        )
    except ValueError as exc:
        message = str(exc)
        status_code = status.HTTP_409_CONFLICT if "already submitted" in message else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=message)

    return _envelope(_to_interest_response(entity, opportunity).model_dump())


@router.get("/api/v1/investments/interests/my")
async def list_my_interests(
    request: Request,
    status_filter: Optional[str] = Query(default=None, alias="status"),
    interest_service: InterestService = Depends(get_interest_service),
    repository: SqlAlchemyInvestmentRepository = Depends(get_investment_repository),
):
    _ensure_role(request, INVESTOR_ROLES)
    interests = await interest_service.list_my_interests(_require_user_id(request), status_filter=status_filter)
    opportunities = await repository.get_opportunities_by_ids([item.opportunity_id for item in interests])
    opportunities_by_id = {item.id: item for item in opportunities}
    payload = [_to_interest_response(item, opportunities_by_id.get(item.opportunity_id)).model_dump() for item in interests]
    return _envelope(payload, meta={"total": len(payload)})


@router.get("/api/v1/investments/opportunities/{opportunity_id}/interests")
async def list_opportunity_interests(
    opportunity_id: str,
    request: Request,
    status_filter: Optional[str] = Query(default=None, alias="status"),
    opportunity_service: OpportunityService = Depends(get_opportunity_service),
    interest_service: InterestService = Depends(get_interest_service),
):
    opportunity = await opportunity_service.get_opportunity(opportunity_id)
    if not opportunity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    user_id = _require_user_id(request)
    if not _can_review(request) and opportunity.owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to view these interests")

    interests = await interest_service.list_opportunity_interests(opportunity_id, status_filter=status_filter)
    payload = [_to_interest_response(item, opportunity).model_dump() for item in interests]
    return _envelope(payload, meta={"total": len(payload)})


@router.patch("/api/v1/investments/interests/{interest_id}/status")
async def update_interest_status(
    interest_id: str,
    body: InterestStatusUpdateRequest,
    request: Request,
    opportunity_service: OpportunityService = Depends(get_opportunity_service),
    interest_service: InterestService = Depends(get_interest_service),
):
    interest = await interest_service.get_interest(interest_id)
    if not interest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interest not found")

    opportunity = await opportunity_service.get_opportunity(interest.opportunity_id)
    if not opportunity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    user_id = _require_user_id(request)
    if not _can_review(request) and opportunity.owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to review this interest")

    updated = await interest_service.update_interest_status(entity=interest, body=body)
    return _envelope(_to_interest_response(updated, opportunity).model_dump())


@router.get("/api/v1/investments/watchlist")
async def get_watchlist(
    request: Request,
    repository: SqlAlchemyInvestmentRepository = Depends(get_investment_repository),
):
    _ensure_role(request, INVESTOR_ROLES)
    entries = await repository.list_watchlist_for_investor(_require_user_id(request))
    opportunity_ids = [entry.opportunity_id for entry in entries]
    opportunities = await repository.get_opportunities_by_ids(opportunity_ids)
    opportunities_by_id = {item.id: item for item in opportunities}
    payload = [
        _to_opportunity_response(opportunities_by_id[opportunity_id], is_watchlisted=True).model_dump()
        for opportunity_id in opportunity_ids
        if opportunity_id in opportunities_by_id
    ]
    return _envelope(payload, meta={"total": len(payload)})


@router.post("/api/v1/investments/watchlist/{opportunity_id}", status_code=status.HTTP_201_CREATED)
async def add_watchlist(
    opportunity_id: str,
    request: Request,
    opportunity_service: OpportunityService = Depends(get_opportunity_service),
    interest_service: InterestService = Depends(get_interest_service),
):
    _ensure_role(request, INVESTOR_ROLES)
    opportunity = await opportunity_service.get_opportunity(opportunity_id)
    if not opportunity or opportunity.status != "open":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    entry = await interest_service.add_watchlist(_require_user_id(request), opportunity_id)
    return _envelope({"id": entry.id, "opportunity_id": opportunity_id})


@router.delete("/api/v1/investments/watchlist/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_watchlist(
    opportunity_id: str,
    request: Request,
    interest_service: InterestService = Depends(get_interest_service),
):
    _ensure_role(request, INVESTOR_ROLES)
    await interest_service.remove_watchlist(_require_user_id(request), opportunity_id)
    return None


@router.get("/api/v1/investments/dashboard")
async def get_dashboard(
    request: Request,
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    repository: SqlAlchemyInvestmentRepository = Depends(get_investment_repository),
):
    _ensure_role(request, INVESTOR_ROLES)
    investor_id = _require_user_id(request)
    data = await dashboard_service.build_dashboard(investor_id)

    watched_ids = await repository.get_watchlisted_opportunity_ids(
        investor_id,
        [item.id for item in data["watchlist"]] + [item.id for item in data["recommended"]],
    )
    related_opportunities = await repository.get_opportunities_by_ids(
        [item.opportunity_id for item in data["recent_interests"]]
    )
    related_by_id = {item.id: item for item in related_opportunities}

    payload = InvestorDashboardResponse(
        status_counts=data["status_counts"],
        recent_interests=[
            _to_interest_response(item, related_by_id.get(item.opportunity_id)) for item in data["recent_interests"]
        ],
        watchlist=[
            _to_opportunity_response(item, is_watchlisted=item.id in watched_ids) for item in data["watchlist"]
        ],
        recommended=[
            _to_opportunity_response(item, is_watchlisted=item.id in watched_ids) for item in data["recommended"]
        ],
    )
    return _envelope(payload.model_dump())
