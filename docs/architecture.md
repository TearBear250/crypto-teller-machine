# CTM Architecture

This document describes the modular architecture of the Crypto Teller Machine (CTM) software and the interfaces between components.

---

## 1. Components Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        CTM Enclosure (Pi)                         │
│                                                                    │
│  ┌─────────────────────┐    Unix socket / IPC   ┌──────────────┐  │
│  │     Kiosk UI        │◄──────────────────────►│Device Daemon │  │
│  │  (Electron/React)   │                        │  (Node/      │  │
│  │                     │                        │   Python)    │  │
│  └──────────┬──────────┘                        └──────┬───────┘  │
│             │ HTTPS / WebSocket                        │ GPIO      │
└─────────────┼────────────────────────────────────────┼───────────┘
              │                                          │
              ▼                                          ▼
  ┌───────────────────────┐                   ┌──────────────────┐
  │   Backend Services    │                   │  Hardware Layer  │
  │  - Payment processor  │                   │  (sensors,       │
  │  - Exchange rate feed │                   │   actuators,     │
  │  - Wallet interface   │                   │   interlocks)    │
  └──────────┬────────────┘                   └──────────────────┘
             │
             ▼
  ┌───────────────────────┐
  │  Monitoring / Alerting│
  │  - Health checks      │
  │  - Cash level alerts  │
  │  - Fault log shipping │
  └───────────────────────┘
```

### 1.1 Kiosk UI (`software/kiosk-ui/`)

- Runs fullscreen on the Raspberry Pi display (Electron shell wrapping a React app).
- Presents the user transaction flow: coin selection → amount entry → cash insert/dispense → confirmation.
- Communicates with the Device Daemon over a local IPC channel (Unix domain socket or named pipe) for hardware state and commands.
- Communicates with Backend Services over HTTPS for exchange rates, payment requests, and transaction confirmation.
- No direct GPIO or hardware access.

### 1.2 Device Daemon (`software/device-daemon/`)

- Runs as a background service on the Pi with appropriate hardware access permissions.
- Owns all GPIO interactions: reads sensors, drives actuators through opto-isolator/driver boards.
- Enforces hardware interlocks (drawer-closed check before dispense enable).
- Implements the **Transaction State Machine** (see Section 3).
- Exposes a command/event IPC interface to the Kiosk UI.
- Manages watchdog heartbeat.
- Logs all state transitions and sensor events.

### 1.3 Backend Services

- Runs on a remote server (or locally in development/test).
- Provides REST/WebSocket API for:
  - Exchange rate queries.
  - Payment invoice creation and status (e.g., BTCPay Server or equivalent open-source backend).
  - Transaction record storage.
- Not directly accessible from the public internet without authentication.

### 1.4 Monitoring and Alerting (`ops/`)

- Collects logs and health metrics from the Pi.
- Alerts operators on: cash level low, dispenser fault, network loss, transaction anomalies.
- Deployment and update pipeline (OTA update mechanism for Pi).

---

## 2. Interface Definitions

### 2.1 Kiosk UI ↔ Device Daemon (IPC)

Communication over a local Unix domain socket using newline-delimited JSON messages.

#### Commands (UI → Daemon)

| Command | Payload | Description |
|---|---|---|
| `START_DISPENSE` | `{ amount_units: N }` | Begin cash-out dispense sequence |
| `CANCEL` | — | Cancel current transaction, return to idle |
| `LOCK_DRAWER` | — | Engage drawer latch |
| `UNLOCK_DRAWER` | — | Release drawer latch for user retrieval |
| `ENABLE_BILL_ACCEPTOR` | — | Allow cash-in |
| `DISABLE_BILL_ACCEPTOR` | — | Stop accepting cash |
| `STATUS_REQUEST` | — | Request current hardware state snapshot |

#### Events (Daemon → UI)

| Event | Payload | Description |
|---|---|---|
| `STATE_CHANGE` | `{ state: <state_name> }` | Daemon state machine transitioned |
| `BILL_INSERTED` | `{ denomination: N }` | Bill acceptor confirmed a bill |
| `DISPENSE_COMPLETE` | `{ units_dispensed: N }` | Dispense cycle finished |
| `DRAWER_OPENED` | — | Drawer open sensor triggered |
| `DRAWER_CLOSED` | — | Drawer closed sensor confirmed |
| `FAULT` | `{ code: <code>, message: <msg> }` | Hardware fault detected |
| `CASH_LEVEL_LOW` | `{ remaining_units: N }` | Cash supply below threshold |

### 2.2 Kiosk UI ↔ Backend Services (HTTPS)

RESTful JSON API over HTTPS (TLS required in production).

| Endpoint | Method | Description |
|---|---|---|
| `/api/rates/{coin}` | GET | Current exchange rate for coin |
| `/api/invoice` | POST | Create a new payment invoice |
| `/api/invoice/{id}` | GET | Poll invoice status |
| `/api/transaction` | POST | Record a completed transaction |

---

## 3. Transaction State Machine

The Device Daemon enforces the following state machine for every transaction.  
No actuator action may occur outside a defined state transition.

```
         ┌─────────┐
    ┌───►│  IDLE   │◄──────────────────────────────────┐
    │    └────┬────┘                                    │
    │         │ UI: ENABLE_BILL_ACCEPTOR /              │
    │         │     START_DISPENSE                      │
    │    ┌────▼──────────┐                              │
    │    │  CASH_IN or   │                              │
    │    │  DISPENSE_    │                              │
    │    │  REQUESTED    │                              │
    │    └────┬──────────┘                              │
    │         │ preconditions met                       │
    │         │ (drawer closed confirmed, etc.)         │
    │    ┌────▼──────────┐                              │
    │    │   RUNNING     │──── sensor fault/jam ───►┌───┴──┐
    │    └────┬──────────┘                          │FAULT │
    │         │ complete                            └───┬──┘
    │    ┌────▼──────────┐                             │
    │    │ AWAITING_     │              authenticated  │
    │    │ RETRIEVAL     │              reset ─────────┘
    │    └────┬──────────┘
    │         │ drawer opened → closed (or timeout)
    └─────────┘
```

### State Descriptions

| State | Description |
|---|---|
| `IDLE` | No active transaction. All actuators in safe default state. |
| `CASH_IN` | Bill acceptor enabled; counting inserted bills. |
| `DISPENSE_REQUESTED` | Cash-out request received; verifying preconditions (drawer closed). |
| `RUNNING` | Actuator(s) active (dispenser running or drawer unlocked for retrieval). |
| `AWAITING_RETRIEVAL` | Dispense complete; drawer unlocked; waiting for user to retrieve cash and close drawer. |
| `FAULT` | Hardware fault, jam, or unexpected sensor state. All actuators halted. Requires authenticated reset. |

---

## 4. Deployment Topology

- **Production:** Pi runs Kiosk UI + Device Daemon; Backend Services run on a hardened remote server or a secured local server.
- **Development:** All components can run on a single developer machine using mock hardware interfaces.
- **Test:** Hardware-in-the-loop test uses real Pi with real GPIO, mock backend services.
