"""HTTP controller for wallet and transactions."""

from __future__ import annotations

from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from core.dependencies import get_wallet_transaction_service
from schemas.requests import CheckoutRequest, PayoutRequest, TopupRequest
from schemas.responses import TransactionResponse, WalletSummaryResponse
from services.wallet_transaction_service import WalletTransactionService


router = APIRouter()

PAYOUT_ROLES = {"guide", "merchant", "admin", "super_admin"}


def _envelope(data: Any = None, meta: Optional[dict] = None, error: Optional[str] = None, success: bool = True) -> dict:
    return {"success": success, "data": data, "meta": meta, "error": error}


def _user_id(request: Request) -> str:
    uid = request.headers.get("X-User-Id")
    if not uid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")
    return uid


def _role(request: Request) -> str:
    return request.headers.get("X-User-Role", "tourist")


def _to_tx(entity) -> TransactionResponse:
    return TransactionResponse(
        id=str(entity.id),
        user_id=entity.user_id,
        tx_type=entity.tx_type,
        direction=entity.direction,
        amount=float(entity.amount),
        balance_after=float(entity.balance_after),
        status=entity.status,
        reference_type=entity.reference_type,
        reference_id=entity.reference_id,
        description=entity.description,
        created_at=entity.created_at,
    )


async def _user_transactions(service: WalletTransactionService, user_id: str) -> list:
    entities = await service.list_entities()
    result = [entity for entity in entities if entity.user_id == user_id]
    result.sort(key=lambda item: item.created_at)
    return result


async def _wallet_summary(service: WalletTransactionService, user_id: str) -> WalletSummaryResponse:
    txs = await _user_transactions(service, user_id)
    total_credit = 0.0
    total_debit = 0.0

    for tx in txs:
        amount = float(tx.amount)
        if tx.direction == "credit":
            total_credit += amount
        else:
            total_debit += amount

    balance = total_credit - total_debit

    return WalletSummaryResponse(
        user_id=user_id,
        currency="EGP",
        balance=round(balance, 2),
        total_credit=round(total_credit, 2),
        total_debit=round(total_debit, 2),
    )


async def _create_transaction(
    service: WalletTransactionService,
    *,
    user_id: str,
    tx_type: str,
    direction: str,
    amount: float,
    balance_after: float,
    status_value: str,
    payment_method: Optional[str] = None,
    description: Optional[str] = None,
    reference_type: Optional[str] = None,
    reference_id: Optional[str] = None,
) -> TransactionResponse:
    entity = await service.create_entity(
        title=f"tx:{user_id}:{tx_type}:{uuid4()}",
        user_id=user_id,
        tx_type=tx_type,
        direction=direction,
        amount=amount,
        balance_after=balance_after,
        status=status_value,
        payment_method=payment_method,
        description=description,
        reference_type=reference_type,
        reference_id=reference_id,
    )
    return _to_tx(entity)


@router.get("/api/v1/wallet")
@router.get("/api/v1/wallet/summary")
async def get_wallet_summary(
    request: Request,
    service: WalletTransactionService = Depends(get_wallet_transaction_service),
):
    summary = await _wallet_summary(service, _user_id(request))
    return _envelope(summary.model_dump())


@router.post("/api/v1/wallet/topup", status_code=status.HTTP_201_CREATED)
async def wallet_topup(
    body: TopupRequest,
    request: Request,
    service: WalletTransactionService = Depends(get_wallet_transaction_service),
):
    uid = _user_id(request)
    summary = await _wallet_summary(service, uid)
    new_balance = summary.balance + body.amount

    tx = await _create_transaction(
        service,
        user_id=uid,
        tx_type="topup",
        direction="credit",
        amount=body.amount,
        balance_after=new_balance,
        status_value="completed",
        payment_method=body.method,
        description=f"Wallet topup via {body.method}",
    )
    return _envelope(tx.model_dump())


@router.post("/api/v1/payments/checkout", status_code=status.HTTP_201_CREATED)
async def checkout(
    body: CheckoutRequest,
    request: Request,
    service: WalletTransactionService = Depends(get_wallet_transaction_service),
):
    uid = _user_id(request)
    summary = await _wallet_summary(service, uid)
    if summary.balance < body.amount:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Insufficient wallet balance")

    new_balance = summary.balance - body.amount
    tx = await _create_transaction(
        service,
        user_id=uid,
        tx_type="checkout",
        direction="debit",
        amount=body.amount,
        balance_after=new_balance,
        status_value="completed",
        payment_method="wallet",
        description=body.description or f"Checkout for {body.reference_type}",
        reference_type=body.reference_type,
        reference_id=body.reference_id,
    )
    return _envelope(tx.model_dump())


@router.post("/api/v1/payments/payouts", status_code=status.HTTP_201_CREATED)
async def request_payout(
    body: PayoutRequest,
    request: Request,
    service: WalletTransactionService = Depends(get_wallet_transaction_service),
):
    uid = _user_id(request)
    role = _role(request)
    if role not in PAYOUT_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role not allowed for payouts")

    summary = await _wallet_summary(service, uid)
    if summary.balance < body.amount:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Insufficient wallet balance")

    new_balance = summary.balance - body.amount
    tx = await _create_transaction(
        service,
        user_id=uid,
        tx_type="payout",
        direction="debit",
        amount=body.amount,
        balance_after=new_balance,
        status_value="pending",
        description=body.note or f"Payout to {body.destination}",
        reference_type="payout_destination",
        reference_id=body.destination,
    )
    return _envelope(tx.model_dump())


@router.get("/api/v1/payments/transactions")
async def list_transactions(
    request: Request,
    status_filter: Optional[str] = Query(default=None, alias="status"),
    service: WalletTransactionService = Depends(get_wallet_transaction_service),
):
    uid = _user_id(request)
    txs = await _user_transactions(service, uid)

    data = []
    for tx in txs:
        if status_filter and tx.status != status_filter:
            continue
        data.append(_to_tx(tx).model_dump())

    data.sort(key=lambda item: item["created_at"], reverse=True)
    return _envelope(data, meta={"total": len(data)})
