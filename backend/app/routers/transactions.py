from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException

from shared.models import (
    QuoteRequest,
    QuoteResponse,
    TxCreateRequest,
    TxEventRequest,
    TxEventResponse,
    TxResponse,
)
from backend.app.db import connect

router = APIRouter(prefix="/v1")

# ---------------------------------------------------------------------------
# Placeholder pricing constants (replace with real exchange integration).
# ---------------------------------------------------------------------------
_PLACEHOLDER_BTC_PRICE_CAD = 100_000.00
_FEE_RATE = 0.02


# ---------------------------------------------------------------------------
# Quotes
# ---------------------------------------------------------------------------

@router.post("/quotes", response_model=QuoteResponse)
def create_quote(req: QuoteRequest) -> QuoteResponse:
    """Return a placeholder price quote valid for 2 minutes."""
    fiat_cad = req.fiat_amount / 100.0
    fee_cad = fiat_cad * _FEE_RATE
    net_cad = max(0.0, fiat_cad - fee_cad)

    if req.side == "buy":
        asset_amount = net_cad / _PLACEHOLDER_BTC_PRICE_CAD
    else:
        # Sell: user sends crypto, receives fiat minus fee
        asset_amount = net_cad / _PLACEHOLDER_BTC_PRICE_CAD

    now = datetime.now(timezone.utc)
    return QuoteResponse(
        quote_id=str(uuid.uuid4()),
        side=req.side,
        asset=req.asset,
        fiat=req.fiat,
        fiat_amount=req.fiat_amount,
        asset_amount=f"{asset_amount:.8f}",
        fee_fiat_amount=int(round(fee_cad * 100)),
        expires_at_utc=now + timedelta(minutes=2),
    )


# ---------------------------------------------------------------------------
# Transactions
# ---------------------------------------------------------------------------

@router.post("/transactions", response_model=TxResponse, status_code=201)
def create_transaction(req: TxCreateRequest) -> TxResponse:
    """Create a new transaction, honouring idempotency_key."""
    conn = connect()
    cur = conn.cursor()
    try:
        row = cur.execute(
            "SELECT * FROM transactions WHERE idempotency_key = ?",
            (req.idempotency_key,),
        ).fetchone()

        if row:
            return _row_to_tx(row)

        tx_id = str(uuid.uuid4())
        status = "awaiting_cash" if req.side == "buy" else "awaiting_deposit"
        now = datetime.now(timezone.utc).isoformat()

        cur.execute(
            """
            INSERT INTO transactions
                (tx_id, status, side, asset, fiat, fiat_amount,
                 payout_address, idempotency_key, created_at_utc)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                tx_id,
                status,
                req.side,
                req.asset,
                req.fiat,
                req.fiat_amount,
                req.payout_address,
                req.idempotency_key,
                now,
            ),
        )
        conn.commit()
        row = cur.execute(
            "SELECT * FROM transactions WHERE tx_id = ?", (tx_id,)
        ).fetchone()
        return _row_to_tx(row)
    finally:
        conn.close()


@router.get("/transactions/{tx_id}", response_model=TxResponse)
def get_transaction(tx_id: str) -> TxResponse:
    conn = connect()
    try:
        row = conn.execute(
            "SELECT * FROM transactions WHERE tx_id = ?", (tx_id,)
        ).fetchone()
    finally:
        conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return _row_to_tx(row)


@router.post(
    "/transactions/{tx_id}/events",
    response_model=TxEventResponse,
    status_code=201,
)
def record_event(tx_id: str, req: TxEventRequest) -> TxEventResponse:
    """Ingest a kiosk hardware event (cash_inserted, cash_dispensed, etc.)."""
    conn = connect()
    cur = conn.cursor()
    try:
        tx_row = cur.execute(
            "SELECT tx_id, status, side FROM transactions WHERE tx_id = ?",
            (tx_id,),
        ).fetchone()
        if not tx_row:
            raise HTTPException(status_code=404, detail="Transaction not found")

        event_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        payload_json = json.dumps(req.payload or {})

        cur.execute(
            """
            INSERT INTO tx_events (event_id, tx_id, event_type, payload_json, recorded_at_utc)
            VALUES (?, ?, ?, ?, ?)
            """,
            (event_id, tx_id, req.event_type, payload_json, now),
        )

        # Advance transaction status based on event
        new_status = _next_status(tx_row["status"], req.event_type)
        if new_status != tx_row["status"]:
            cur.execute(
                "UPDATE transactions SET status = ? WHERE tx_id = ?",
                (new_status, tx_id),
            )

        conn.commit()
        return TxEventResponse(
            event_id=event_id,
            tx_id=tx_id,
            event_type=req.event_type,
            recorded_at_utc=datetime.fromisoformat(now),
        )
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _row_to_tx(row: sqlite3.Row) -> TxResponse:  # type: ignore[name-defined]
    return TxResponse(
        tx_id=row["tx_id"],
        status=row["status"],
        side=row["side"],
        asset=row["asset"],
        fiat=row["fiat"],
        fiat_amount=row["fiat_amount"],
        payout_address=row["payout_address"],
        created_at_utc=datetime.fromisoformat(row["created_at_utc"]),
    )


def _next_status(current: str, event_type: str) -> str:
    transitions: dict[tuple[str, str], str] = {
        ("awaiting_cash", "cash_inserted"): "executing",
        ("executing", "cash_dispensed"): "completed",
        ("awaiting_deposit", "deposit_confirmed"): "dispensing",
        ("dispensing", "cash_dispensed"): "completed",
        ("executing", "receipt_printed"): "completed",
    }
    return transitions.get((current, event_type), current)
