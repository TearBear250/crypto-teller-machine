# Architecture Overview

## 1. System Summary

The **Crypto Teller Machine (CTM / LTM)** is a non-custodial altcoin teller machine that
lets end-users exchange cash for cryptocurrency (buy) or exchange cryptocurrency for cash
(sell). End-users scan their own wallet address; the machine never holds private keys on
behalf of users.

### Target assets (v1 scope)
| Asset | Network | Notes |
|-------|---------|-------|
| LTC   | Litecoin | UTXO-based; primary asset |
| DOGE  | Dogecoin | UTXO-based |
| XRP   | XRP Ledger | Account-based; destination-tag required |
| SOL   | Solana | Account-based; devnet first |

---

## 2. High-Level Components

```
┌──────────────────────────────────────────────────────────────────────┐
│                          KIOSK (Fedora)                               │
│                                                                        │
│  ┌─────────────┐  ┌───────────────┐  ┌──────────────────────────┐    │
│  │  kiosk-ui   │  │  kiosk-agent  │  │        ltm-hal           │    │
│  │ (touch UI)  │◄─┤ (state machine│  │  bill validator          │    │
│  │             │  │  + local cache│  │  cash dispenser          │    │
│  └──────┬──────┘  └──────┬────────┘  │  QR scanner / camera     │    │
│         │                │           │  receipt printer          │    │
│         └────────────────┘           └──────────────────────────┘    │
│                  │  REST over mTLS                                     │
└──────────────────┼─────────────────────────────────────────────────-──┘
                   │
                   ▼ (outbound only, port 443 / 8443)
┌──────────────────────────────────────────────────────────────────────┐
│                    BACKEND SERVER FARM (CentOS Stream 9)              │
│                                                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐      │
│  │  backend-api │  │  chain-relay │  │  fleet-mgmt            │      │
│  │  (quotes,    │  │  (LTC/DOGE   │  │  (device registry,     │      │
│  │   sessions,  │  │   XRP / SOL  │  │   config push,         │      │
│  │   audit)     │  │   nodes/RPC) │  │   health)              │      │
│  └──────┬───────┘  └──────┬───────┘  └────────────────────────┘      │
│         └─────────────────┘                                           │
│                  │ (internal bus / DB)                                 │
│         ┌────────▼────────┐                                           │
│         │  PostgreSQL /   │                                           │
│         │  TimescaleDB    │                                           │
│         └─────────────────┘                                           │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 3. Component Responsibilities

### 3.1 Kiosk (Fedora)

| Component | Role |
|-----------|------|
| `kiosk-ui` | Full-screen touch interface (buy / sell flows, QR scan prompts, receipts) |
| `kiosk-agent` | Transaction state machine; talks to backend-api; local session cache for disconnect resilience |
| `ltm-hal` | Hardware Abstraction Layer — adapters for bill acceptor (MDB/ccTalk), cash dispenser, receipt printer, QR/camera |

### 3.2 Backend (CentOS Stream 9)

| Service | Role |
|---------|------|
| `backend-api` | REST API (OpenAPI spec at `shared/contracts/openapi.yaml`); sessions, quotes, audit |
| `chain-relay` | Pluggable chain connectors; validates addresses, creates transactions, monitors confirmations |
| `fleet-mgmt` | Device registration, per-device config, signed update delivery, health heartbeats |
| PostgreSQL | Persistent store for sessions, audit events, device records |

---

## 4. Data Flow — Cash-In (Buy Crypto)

```
User inserts bill(s)
      │
      ▼
ltm-hal: bill-accepted event ──► kiosk-agent
      │                                │
      │               POST /sessions (amount, asset, kiosk-id)
      │                                │
      │                         backend-api
      │                                │
      │                    GET quote (rate + fee)
      │                         chain-relay
      │                                │
      ◄──────── quote response ─────────
      │
      ▼
kiosk-ui: "You receive X LTC — scan address"
      │
User scans QR address
      │
      ▼
kiosk-agent ──► POST /sessions/{id}/confirm (address, accepted)
                       │
                 backend-api ──► chain-relay: broadcast tx
                       │
                 track confirmations (risk policy)
                       │
                 PATCH /sessions/{id}/state = COMPLETE
                       │
kiosk-agent ◄──────────┘
      │
ltm-hal: print receipt
```

---

## 5. Plugin Model for Multi-Chain

Each supported chain is implemented as a **chain plugin** that satisfies a common interface:

```
interface ChainPlugin {
  validateAddress(input: string): ValidationResult
  getQuote(fiatAmount: Decimal, fiatCurrency: string): QuoteResult
  buildPayoutTx(destination: string, amount: Decimal): Transaction
  broadcastTx(tx: Transaction): string          // returns txid
  trackTx(txid: string): TxStatus
  requiredConfirmations(amount: Decimal): number // risk policy
}
```

Plugins are loaded by `chain-relay` at startup via a plugin registry. Adding a new asset
requires only implementing this interface and registering the plugin — no changes to the
core API.

### Implemented / Planned Plugins

| Plugin | Status | Notes |
|--------|--------|-------|
| `ltc` | Planned (Alpha) | LTC testnet first |
| `doge` | Planned (Alpha) | Dogecoin testnet |
| `xrp` | Planned (Beta) | Requires destination-tag UX |
| `sol` | Planned (Beta) | Solana devnet first |

---

## 6. Deployment Topology

```
┌───────────────────────────────────────────────────────────────┐
│  Canada (testnet region)                                       │
│                                                                │
│  ┌──────────────────┐      ┌──────────────────────────────┐   │
│  │  LTM Kiosk       │      │  LTM Kiosk                   │   │
│  │  Fedora (x86_64) │      │  Fedora (aarch64 / Pi 5)     │   │
│  └────────┬─────────┘      └────────┬─────────────────────┘   │
│           │                         │                          │
│           └───────────┬─────────────┘                         │
│                       │ mTLS                                   │
│           ┌───────────▼─────────────────┐                     │
│           │  Backend Server Farm        │                     │
│           │  CentOS Stream 9 / RHEL-9   │                     │
│           │  (bare-metal or cloud VM)   │                     │
│           └─────────────────────────────┘                     │
└───────────────────────────────────────────────────────────────┘
```

**Modes:**
- **Testnet/Devnet** — Alpha; Canada test region; no real funds
- **Mainnet** — Beta and beyond; additional compliance steps required

---

## 7. Technology Stack Summary

| Layer | Technology |
|-------|-----------|
| Kiosk OS | Fedora (IoT edition or Workstation in kiosk mode) |
| Backend OS | CentOS Stream 9 (RHEL ecosystem) |
| Containers | Podman (rootless) |
| Service manager | systemd + `podman-auto-update` |
| API contract | OpenAPI 3.0 (REST) — see `shared/contracts/openapi.yaml` |
| Transport security | mTLS (device certificates issued per-kiosk) |
| Database | PostgreSQL (TimescaleDB extension for time-series audit data) |
| Chain connectivity | Per-plugin RPC clients |

---

## 8. Key Design Principles

1. **Non-custodial first** — The machine never holds, derives, or transmits user private keys.
2. **Offline resilience** — The kiosk-agent caches pending sessions locally; cash is not
   committed until the backend confirms (or a safe timeout/reject path is taken).
3. **Plugin architecture** — New chains are plugins, not core changes.
4. **Pluggable transport** — Backend URL is configurable; satellite/alternative transport
   can be swapped by changing the transport provider without changing business logic.
5. **Audit trail** — Every cash and crypto event is logged immutably (append-only) before
   any hardware action is taken.
6. **Least privilege** — Kiosk services run as non-root in containers; SELinux enforcing
   on both Fedora and CentOS.
