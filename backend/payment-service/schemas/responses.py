"""Payment response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class WalletSummaryResponse(BaseModel):
    user_id: str
    currency: str
    balance: float
    total_credit: float
    total_debit: float


class TransactionResponse(BaseModel):
    id: str
    user_id: str
    tx_type: str
    direction: str
    amount: float
    balance_after: float
    status: str
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime