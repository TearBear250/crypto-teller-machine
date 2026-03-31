# API Reference

## Overview

The kiosk-agent communicates with the backend over a **REST API** defined in
`shared/contracts/openapi.yaml` (OpenAPI 3.0). All endpoints require **mTLS**
(mutual TLS) — the kiosk presents its device certificate on every request.

> **gRPC note:** A gRPC/Protobuf transport is a viable alternative to REST for
> lower-latency streaming (e.g., real-time confirmation tracking). The OpenAPI spec
> can be evolved into a proto definition without changing the logical API surface.
> gRPC adoption is deferred to a future milestone.

---

## Base URL

| Environment | Base URL |
|-------------|----------|
| Development (local) | `https://localhost:8443/v1` |
| Testnet (Canada) | `https://backend.ctm.internal:8443/v1` |
| Production | TBD |

---

## Authentication

All requests must present a valid device certificate (mTLS). The backend validates:
1. The certificate was issued by the fleet CA.
2. The `CN` matches a registered `kiosk_id`.
3. The certificate is not expired or revoked.

No additional API key is required — the device certificate IS the credential.

---

## Resource Summary

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness / readiness check |
| `GET` | `/assets` | List supported assets |
| `GET` | `/assets/{assetId}/quote` | Get exchange rate quote |
| `POST` | `/sessions` | Create a new transaction session |
| `GET` | `/sessions/{sessionId}` | Get session state |
| `POST` | `/sessions/{sessionId}/confirm` | Confirm session (lock quote + submit address) |
| `POST` | `/sessions/{sessionId}/cancel` | Cancel a session (return cash) |
| `GET` | `/sessions/{sessionId}/status` | Poll transaction status (confirmations) |
| `POST` | `/audit/events` | Append audit event (from kiosk) |
| `GET` | `/fleet/config` | Fetch current kiosk config / policy |
| `POST` | `/fleet/heartbeat` | Device health heartbeat |

Full request/response schemas are defined in `shared/contracts/openapi.yaml`.

---

## Key Flows

### Cash-In (Buy Crypto)

```
1. GET /assets/{assetId}/quote?fiat_amount=100&fiat_currency=CAD
   → returns: asset_amount, rate, fee, quote_id, expires_at

2. POST /sessions
   body: { kiosk_id, direction: "buy", asset_id, fiat_amount, fiat_currency, quote_id }
   → returns: session_id, state: "AWAITING_CASH"

3. (kiosk: bill acceptor accepts cash, HAL event fired)

4. POST /sessions/{id}/confirm
   body: { destination_address, destination_tag? }
   → returns: state: "PROCESSING", txid (pending)

5. GET /sessions/{id}/status  (poll or SSE)
   → returns: state, confirmations, txid, completed_at
```

### Cash-Out (Sell Crypto)

```
1. GET /assets/{assetId}/quote?asset_amount=1.5&fiat_currency=CAD
   → returns: fiat_amount, rate, fee, quote_id, expires_at

2. POST /sessions
   body: { kiosk_id, direction: "sell", asset_id, asset_amount, fiat_currency, quote_id }
   → returns: session_id, state: "AWAITING_CRYPTO", deposit_address, destination_tag?

3. (user sends crypto to deposit_address)

4. GET /sessions/{id}/status  (poll — backend monitors for incoming tx)
   → state transitions: AWAITING_CRYPTO → CONFIRMING → CONFIRMED → DISPENSING → COMPLETE

5. Once state = DISPENSING:
   → kiosk-agent instructs ltm-hal to dispense cash
   → POST /audit/events { type: "CASH_DISPENSED", session_id, amount, currency }
```

---

## Error Responses

All errors follow a standard envelope:

```json
{
  "error": {
    "code": "QUOTE_EXPIRED",
    "message": "The quote has expired. Request a new quote.",
    "request_id": "req-abc123"
  }
}
```

### Standard Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `QUOTE_EXPIRED` | 409 | Quote TTL exceeded; request fresh quote |
| `ADDRESS_INVALID` | 422 | Destination address failed validation |
| `ASSET_DISABLED` | 403 | Asset is not currently enabled on this kiosk |
| `LIMIT_EXCEEDED` | 422 | Transaction exceeds per-session or daily limit |
| `SESSION_NOT_FOUND` | 404 | Unknown session ID |
| `DEVICE_NOT_REGISTERED` | 401 | Device certificate not recognized |
| `INTERNAL_ERROR` | 500 | Unhandled server error |

---

## Audit Events

The kiosk posts audit events for every significant hardware and software action.
Event types include:

| Event Type | Trigger |
|-----------|---------|
| `BILL_INSERTED` | Bill acceptor accepted a note |
| `BILL_REJECTED` | Bill acceptor rejected a note |
| `CASH_DISPENSED` | Cash dispenser released notes |
| `QR_SCANNED` | User scanned a wallet address |
| `SESSION_CREATED` | New session started |
| `SESSION_CONFIRMED` | Address submitted, tx broadcast requested |
| `SESSION_CANCELLED` | Session cancelled (cash returned or timeout) |
| `SESSION_COMPLETED` | Transaction fully confirmed |
| `HAL_ERROR` | Hardware error on any device |
| `OPERATOR_LOGIN` | Operator mode entered |
| `CONFIG_UPDATED` | Config fetched from fleet-mgmt |

---

## OpenAPI Spec

The full machine-readable spec is at:

```
shared/contracts/openapi.yaml
```

You can render it locally with:

```bash
# Using Swagger UI via Podman
podman run --rm -p 8090:8080 \
  -e SWAGGER_JSON=/spec/openapi.yaml \
  -v $(pwd)/shared/contracts:/spec:ro \
  docker.io/swaggerapi/swagger-ui
# Then open http://localhost:8090
```
