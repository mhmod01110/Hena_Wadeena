"""Payment request schemas."""

from pydantic import BaseModel, Field
from typing import Optional, Literal


class TopupRequest(BaseModel):
    amount: float = Field(..., gt=0)
    method: Literal["visa", "mastercard", "wallet", "bank"] = "visa"


class CheckoutRequest(BaseModel):
    amount: float = Field(..., gt=0)
    reference_type: str = Field(..., min_length=2, max_length=50)
    reference_id: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(default=None, max_length=1000)


class PayoutRequest(BaseModel):
    amount: float = Field(..., gt=0)
    destination: str = Field(..., min_length=2, max_length=100)
    note: Optional[str] = Field(default=None, max_length=500)