"""Mock payment/wallet endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

WALLET = {
    "id": "w-001", "user_id": "b2c3d4e5",
    "balance": 2500.00, "currency": "EGP",
}

TRANSACTIONS = [
    {
        "id": "tx-001", "type": "topup", "amount": 5000, "direction": "credit",
        "balance_after": 5000, "description": "شحن المحفظة — فيزا",
        "status": "completed", "created_at": "2026-03-01T10:00:00",
    },
    {
        "id": "tx-002", "type": "booking_pay", "amount": 1600, "direction": "debit",
        "balance_after": 3400, "reference_type": "booking", "reference_id": "bk-002",
        "description": "دفع حجز — جولة آثار الخارجة",
        "status": "completed", "created_at": "2026-03-05T14:30:00",
    },
    {
        "id": "tx-003", "type": "booking_pay", "amount": 900, "direction": "debit",
        "balance_after": 2500, "reference_type": "booking", "reference_id": "bk-001",
        "description": "عربون حجز — سفاري الصحراء البيضاء",
        "status": "completed", "created_at": "2026-03-06T09:00:00",
    },
]


class TopupRequest(BaseModel):
    amount: float
    method: str = "visa"


@router.get("/wallet")
def get_wallet():
    return {"success": True, "data": {**WALLET, "recent_transactions": TRANSACTIONS[:3]}}


@router.post("/wallet/topup")
def topup(body: TopupRequest):
    WALLET["balance"] += body.amount
    tx = {
        "id": f"tx-{len(TRANSACTIONS)+1:03d}", "type": "topup",
        "amount": body.amount, "direction": "credit",
        "balance_after": WALLET["balance"],
        "description": f"شحن المحفظة — {body.method}",
        "status": "completed", "created_at": "2026-03-07T15:00:00",
    }
    TRANSACTIONS.insert(0, tx)
    return {"success": True, "message": f"تم شحن {body.amount} جنيه بنجاح",
            "data": {"new_balance": WALLET["balance"]}}


@router.get("/transactions")
def get_transactions():
    return {"success": True, "data": TRANSACTIONS}
