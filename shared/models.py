from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

Side = Literal["buy", "sell"]

TxStatus = Literal[
    "created",
    "awaiting_cash",
    "cash_inserted",
    "executing",
    "completed",
    "failed",
    "canceled",
    "awaiting_deposit",
    "deposit_confirmed",
    "dispensing",
    "cash_dispensed",
]

KioskEventType = Literal[
    "cash_inserted",
    "cash_dispensed",
    "receipt_printed",
    "deposit_confirmed",
    "error",
]


class Health(BaseModel):
    status: str = "ok"
    time_utc: datetime


class QuoteRequest(BaseModel):
    side: Side
    asset: str = "BTC"
    fiat: str = "CAD"
    fiat_amount: int = Field(ge=1, description="Fiat amount in cents")


class QuoteResponse(BaseModel):
    quote_id: str
    side: Side
    asset: str
    fiat: str
    fiat_amount: int
    asset_amount: str
    fee_fiat_amount: int
    expires_at_utc: datetime


class TxCreateRequest(BaseModel):
    side: Side
    asset: str = "BTC"
    fiat: str = "CAD"
    fiat_amount: int = Field(ge=1)
    idempotency_key: str
    payout_address: Optional[str] = None


class TxResponse(BaseModel):
    tx_id: str
    status: TxStatus
    side: Side
    asset: str
    fiat: str
    fiat_amount: int
    payout_address: Optional[str] = None
    created_at_utc: datetime


class TxEventRequest(BaseModel):
    event_type: KioskEventType
    payload: Optional[dict] = None


class TxEventResponse(BaseModel):
    event_id: str
    tx_id: str
    event_type: KioskEventType
    recorded_at_utc: datetime
