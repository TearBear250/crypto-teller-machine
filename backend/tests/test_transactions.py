"""Unit tests for transaction creation (idempotency) and event recording."""
from __future__ import annotations

import uuid


def _idem() -> str:
    return str(uuid.uuid4())


def _make_tx(client, side: str = "buy", fiat_amount: int = 10000, idem: str | None = None):
    payload = {
        "side": side,
        "asset": "BTC",
        "fiat": "CAD",
        "fiat_amount": fiat_amount,
        "idempotency_key": idem or _idem(),
    }
    return client.post("/v1/transactions", json=payload)


# ---------------------------------------------------------------------------
# Create transaction
# ---------------------------------------------------------------------------

def test_create_buy_transaction(client):
    resp = _make_tx(client, side="buy")
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "awaiting_cash"
    assert data["side"] == "buy"
    assert "tx_id" in data


def test_create_sell_transaction(client):
    resp = _make_tx(client, side="sell")
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "awaiting_deposit"
    assert data["side"] == "sell"


def test_get_transaction(client):
    resp = _make_tx(client)
    tx_id = resp.json()["tx_id"]
    get_resp = client.get(f"/v1/transactions/{tx_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["tx_id"] == tx_id


def test_get_unknown_transaction_returns_404(client):
    resp = client.get("/v1/transactions/does-not-exist")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Idempotency
# ---------------------------------------------------------------------------

def test_idempotency_returns_same_tx(client):
    key = _idem()
    resp1 = _make_tx(client, idem=key)
    resp2 = _make_tx(client, idem=key)
    assert resp1.status_code == 201
    # Second call returns existing tx (200 or 201, body must match)
    assert resp1.json()["tx_id"] == resp2.json()["tx_id"]
    assert resp1.json()["status"] == resp2.json()["status"]


def test_idempotency_different_keys_create_different_txs(client):
    resp1 = _make_tx(client)
    resp2 = _make_tx(client)
    assert resp1.json()["tx_id"] != resp2.json()["tx_id"]


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

def test_record_cash_inserted_event(client):
    tx_id = _make_tx(client).json()["tx_id"]
    ev_resp = client.post(
        f"/v1/transactions/{tx_id}/events",
        json={"event_type": "cash_inserted"},
    )
    assert ev_resp.status_code == 201
    assert ev_resp.json()["event_type"] == "cash_inserted"


def test_event_advances_status(client):
    tx_id = _make_tx(client, side="buy").json()["tx_id"]

    # cash_inserted moves buy tx from awaiting_cash → executing
    client.post(f"/v1/transactions/{tx_id}/events", json={"event_type": "cash_inserted"})
    status = client.get(f"/v1/transactions/{tx_id}").json()["status"]
    assert status == "executing"


def test_sell_event_flow(client):
    tx_id = _make_tx(client, side="sell").json()["tx_id"]

    client.post(f"/v1/transactions/{tx_id}/events", json={"event_type": "deposit_confirmed"})
    assert client.get(f"/v1/transactions/{tx_id}").json()["status"] == "dispensing"

    client.post(f"/v1/transactions/{tx_id}/events", json={"event_type": "cash_dispensed"})
    assert client.get(f"/v1/transactions/{tx_id}").json()["status"] == "completed"


def test_event_on_unknown_tx_returns_404(client):
    resp = client.post(
        "/v1/transactions/no-such-tx/events",
        json={"event_type": "cash_inserted"},
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Quotes
# ---------------------------------------------------------------------------

def test_create_quote_buy(client):
    resp = client.post(
        "/v1/quotes",
        json={"side": "buy", "asset": "BTC", "fiat": "CAD", "fiat_amount": 10000},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["side"] == "buy"
    assert float(data["asset_amount"]) > 0
    assert data["fee_fiat_amount"] > 0


def test_create_quote_sell(client):
    resp = client.post(
        "/v1/quotes",
        json={"side": "sell", "asset": "BTC", "fiat": "CAD", "fiat_amount": 5000},
    )
    assert resp.status_code == 200
    assert resp.json()["side"] == "sell"
