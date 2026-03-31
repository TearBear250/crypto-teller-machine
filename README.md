# Crypto Teller Machine (CTM)

A Raspberry Pi–based kiosk concept for buying and selling cryptocurrency with physical cash.  
**Status: early design / scaffold — no production code yet.**

---

## What is the CTM?

The CTM is an open-source kiosk project that lets users:

- **Cash in** — insert banknotes and receive cryptocurrency to a wallet address or printed/on-screen QR code.
- **Cash out** — send cryptocurrency and receive banknotes dispensed into a secured drawer pocket.
- **Collect a souvenir token** — receive a non-monetary, collectible token branded with a supported coin's icon (see [Souvenir Token Policy](#souvenir-token-policy) below).

Target hardware platform: **Raspberry Pi (ARM)** running a locked-down Linux kiosk OS.  
Multi-coin support is planned (BTC, LTC, DOGE, XRP, SOL, and others via backend plugins).

---

## Safety Principles

Physical safety is a first-class requirement in this project.

| Principle | Summary |
|---|---|
| **No user access to moving parts** | All actuators (bill transport, dispenser, receipt cutter) are behind internal barriers. |
| **Drawer-style payout pocket** | Cash is dispensed into a two-chamber drawer; the user pulls the drawer to retrieve bills rather than reaching into a slot. |
| **Anti-entanglement** | No exposed rollers, belts, or gears. Openings use brush gaskets and minimum-gap geometry to prevent hair, clothing, or fingers from reaching mechanisms. |
| **Hardware interlocks** | Dispenser power is gated by a hardware drawer-closed signal, independent of software state. |
| **Fail-safe defaults** | On boot, reset, or software fault, all actuators default to the OFF/locked state. |
| **Fault handling** | A transaction state machine stops motion on any jam or unexpected sensor state and parks the system in a recoverable safe state. |

See [`docs/safety.md`](docs/safety.md) and [`docs/gpio-safety.md`](docs/gpio-safety.md) for full requirements.

---

## Souvenir Token Policy

The CTM may dispense **physical souvenir tokens** as a collectible novelty.

> **These tokens have absolutely no cash value, are not legal tender, carry no monetary denomination, and cannot be redeemed for cash, cryptocurrency, or any goods or services.**  
> They are collectibles only — similar to a commemorative coin or arcade token — and are labeled as such.

Tokens display coin brand icons (e.g., Litecoin "Ł", Dogecoin "Ð") as visual identifiers, never as a statement of value.  
See [`docs/token-dispenser.md`](docs/token-dispenser.md) for full labeling and design constraints.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────┐
│                   CTM Enclosure                      │
│                                                      │
│  ┌──────────────┐     IPC      ┌──────────────────┐  │
│  │  Kiosk UI    │◄────────────►│  Device Daemon   │  │
│  │  (Electron / │             │  (GPIO, sensors,  │  │
│  │   React)     │             │   actuators,      │  │
│  └──────┬───────┘             │   interlocks)     │  │
│         │ HTTPS/WS            └──────────────────┘  │
└─────────┼───────────────────────────────────────────┘
          │
          ▼
┌─────────────────────┐     ┌───────────────────────┐
│   Backend Services  │────►│  Monitoring / Alerting │
│  (payment, wallet,  │     │  (health, cash levels, │
│   exchange rates)   │     │   fault logs)          │
└─────────────────────┘     └───────────────────────┘
```

| Component | Location | Responsibility |
|---|---|---|
| Kiosk UI | `software/kiosk-ui/` | Full-screen touch interface, transaction flow |
| Device Daemon | `software/device-daemon/` | GPIO, interlocks, actuator control, state machine |
| Backend Services | TBD (separate service) | Payment processing, exchange rates, wallet management |
| Monitoring | `ops/` | Deployment, health checks, alerting |

See [`docs/architecture.md`](docs/architecture.md) for interface definitions and the transaction state machine.

---

## Repository Structure

```
crypto-teller-machine/
├── docs/
│   ├── safety.md           # Physical safety requirements and design checklist
│   ├── gpio-safety.md      # Raspberry Pi GPIO safety guidelines
│   ├── architecture.md     # Modular architecture and state machine
│   └── token-dispenser.md  # Souvenir token dispenser requirements
├── hardware/
│   └── README.md           # BOM and enclosure design notes
├── software/
│   ├── kiosk-ui/
│   │   └── README.md       # Kiosk UI placeholder
│   └── device-daemon/
│       └── README.md       # Device daemon placeholder
├── ops/
│   └── README.md           # Deployment and monitoring plan
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── LICENSE
└── README.md
```

---

## MVP Milestones

| Milestone | Description |
|---|---|
| **M0 – Scaffold** | Repository structure, documentation, safety requirements (this milestone) |
| **M1 – Hardware Prototype** | Enclosure design, BOM finalized, drawer mechanism and interlocks validated |
| **M2 – Device Daemon** | GPIO state machine, interlock logic, sensor polling, safe defaults |
| **M3 – Kiosk UI Shell** | Fullscreen kiosk app, transaction flow screens, PIN/QR input |
| **M4 – Backend Integration** | Exchange rate feed, payment processing, wallet interface |
| **M5 – Integration Test** | End-to-end cash-in/cash-out flow on real hardware in test enclosure |
| **M6 – Safety Audit** | Independent review of mechanical, electrical, and software safety |

---

## Non-Goals (for MVP)

- No KYC/ID scanning in initial scope (design must allow future addition).
- No cloud custody of private keys.
- No proprietary vendor SDKs — only open protocols (MDB, ccTalk, ESC/POS, standard serial/USB).
- No monetary denomination on souvenir tokens.
- No network services exposed without authentication.

---

## Contributing

Please read [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) before contributing.  
To report a security issue, see [`SECURITY.md`](SECURITY.md).

---

## License

[MIT](LICENSE) — Copyright (c) 2026 Spartan 099

