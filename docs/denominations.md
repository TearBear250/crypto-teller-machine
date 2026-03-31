# Denomination Stability Guide

This document explains **why integer cents are mandatory** across the CTM/LTM
fleet, how denomination IDs work, and the rule that every kiosk **must render
denominations from config only**.

---

## Why Integer Cents Are Required

Fiat amounts inside a crypto teller machine travel through many systems: the
bill acceptor firmware, the kiosk-agent, the backend API, audit logs, printed
vouchers, and QR payloads.  Each system may use a different programming
language or floating-point implementation.

**Example of the problem with floats:**

```python
>>> 0.10 + 0.20
0.30000000000000004   # Python
```

When `$20.00` is stored as `20.0` (double), it may round-trip as
`19.999999999999996` in a different language.  Multiplied across thousands of
daily transactions and dozens of kiosks, these discrepancies cause:

- Kiosks accepting or rejecting a bill they shouldn't.
- QR-encoded amounts mismatching voucher face values.
- Audit reconciliation failures.

**The fix: always store fiat amounts as integer cents.**

| Human value | Float (risky) | Integer cents (safe) |
|-------------|--------------|----------------------|
| $1.00       | 1.0          | 100                  |
| $0.25       | 0.25         | 25                   |
| $0.10       | 0.1          | 10                   |
| $100.00     | 100.0        | 10000                |
| $1,000.00   | 1000.0       | 100000               |

The `MoneyCents` schema enforces `type: integer, minimum: 0`.  Any field
carrying a fiat amount **must** use this type.  The legacy `fiat_amount`
(double) fields in the OpenAPI spec are marked `deprecated` and will be
removed in a future API version.

---

## Stable Denomination IDs

Every denomination has a **stable ID** that:

- Is assigned **once** and **never changes**, even if the display label or
  theme is updated.
- Uniquely identifies the denomination across all kiosk software versions.
- Is the canonical key used in audit events (`BILL_INSERTED`, `CASH_DISPENSED`)
  and in printed vouchers.

### ID format

```
{KIND}_{CURRENCY}_{VALUE_CENTS_ZERO_PADDED}
```

| Example ID         | Kind | Currency | Value cents | Human value |
|--------------------|------|----------|-------------|-------------|
| `BILL_USD_100`     | BILL | USD      | 100         | $1.00       |
| `BILL_USD_500`     | BILL | USD      | 500         | $5.00       |
| `BILL_USD_10000`   | BILL | USD      | 10000       | $100.00     |
| `COIN_USD_025`     | COIN | USD      | 25          | $0.25       |
| `COIN_USD_001`     | COIN | USD      | 1           | $0.01       |

> **Rule:** The numeric suffix is the raw `value_cents` integer, not
> zero-padded to a fixed width.  For example, 25 cents is `025` and 1 cent
> is `001` only for readability in the USD default set.  New IDs should
> follow the same convention for the currency.

### Why stability matters

If an ID were ever renamed (e.g., `BILL_USD_100` → `BILL_USD_1_00`), kiosks
running old software would fail to match bills against the config and could
refuse valid currency.  **Never rename or recycle an ID.**

If a denomination is retired, set `"enabled": false`.  Do not delete it from
the config file.

---

## Denomination Sets

A **DenominationSet** (`shared/schemas/denomination_set.schema.json`) groups
all bills and coins for a single fiat currency.  It carries a `spec_version`
(format `YYYY-MM-DD.N`) so kiosks can detect and refuse downgrade attempts.

The initial USD configuration is at `shared/denominations/usd_default.json`.

### Bills (USD default)

| ID               | Value cents | Display |
|------------------|-------------|---------|
| BILL_USD_100     | 100         | $1      |
| BILL_USD_500     | 500         | $5      |
| BILL_USD_1000    | 1000        | $10     |
| BILL_USD_2000    | 2000        | $20     |
| BILL_USD_5000    | 5000        | $50     |
| BILL_USD_10000   | 10000       | $100    |
| BILL_USD_100000  | 100000      | $1000   |

### Coins (USD default)

| ID            | Value cents | Display |
|---------------|-------------|---------|
| COIN_USD_001  | 1           | 1¢      |
| COIN_USD_005  | 5           | 5¢      |
| COIN_USD_010  | 10          | 10¢     |
| COIN_USD_025  | 25          | 25¢     |
| COIN_USD_050  | 50          | 50¢     |
| COIN_USD_100  | 100         | $1      |
| COIN_USD_200  | 200         | $2      |

---

## Kiosks Must Render From Config Only

A kiosk **must not hard-code denomination values** in its source code.  The
correct workflow is:

1. On startup, fetch `KioskConfig` from `/fleet/config`.
2. Validate `KioskConfig.denominations.spec_version` is ≥ the last seen
   version.  Refuse to operate if it is lower (downgrade attack prevention).
3. Build the denomination UI entirely from the `bills` and `coins` arrays in
   the received `DenominationSet`.
4. When logging an audit event for a bill or coin, use the denomination `id`
   field, not the display label.

This guarantees that:

- All kiosks in the fleet show identical denominations at all times.
- A denomination can be enabled/disabled fleet-wide by pushing a new config
  with `"enabled": false` — no software update required.
- QR-encoded vouchers reference denomination IDs that are stable across all
  kiosk versions.

---

## Adding a New Denomination

1. Choose a new stable ID following the naming convention.
2. Add the denomination object to the appropriate array (`bills` or `coins`)
   in `shared/denominations/usd_default.json` (or the relevant currency file).
3. Increment `spec_version` (e.g., `2026-03-31.1` → `2026-04-01.1`).
4. Deploy the updated config via `/fleet/config`.  Kiosks will pick it up on
   their next config poll.

**Never** remove a denomination that any in-service kiosk may have seen.
Disable it with `"enabled": false` instead.
