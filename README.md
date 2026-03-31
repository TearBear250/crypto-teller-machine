# Crypto Teller Machine (CTM / LTM)

A non-custodial **altcoin teller machine** — cash in/out for Litecoin, Dogecoin, XRP,
Solana, and more. Built on open-source components with a clear separation between the
**Fedora kiosk terminal** and the **CentOS Stream 9 backend server farm**.

> **Status:** Architecture skeleton / Alpha scaffold. No real crypto or cash logic yet.
> Canada is the testnet region for Alpha development.

---

## Repository Structure

```
crypto-teller-machine/
├── kiosk/                  # Fedora kiosk terminal (kiosk-agent, ltm-hal, kiosk-ui)
├── backend/                # CentOS Stream 9 backend (backend-api, chain-plugins)
├── shared/
│   ├── contracts/          # OpenAPI 3.0 spec (openapi.yaml)
│   └── schemas/            # JSON schemas: transaction, session, audit-event
├── deploy/
│   ├── containers/         # Containerfiles + podman-compose
│   └── systemd/            # systemd unit files for Podman-managed services
├── docs/
│   ├── architecture.md     # High-level components, data flow, plugin model
│   ├── deployment.md       # Fedora kiosk + CentOS Stream 9 backend deployment guide
│   ├── api.md              # API reference (REST + OpenAPI)
│   └── security.md         # Security baseline (mTLS, audit logging, risk policy)
├── ROADMAP.md              # Alpha → Beta → Delta/Omega/Theta milestones
├── LICENSE                 # MIT
└── README.md               # This file
```

---

## Quick Start (Simulator Mode — no hardware required)

### Prerequisites

- Podman 4.x (`sudo dnf install -y podman podman-compose`)
- Fedora 39+ (kiosk) or CentOS Stream 9 (backend)

### Run the backend + kiosk agent locally

```bash
git clone https://github.com/TearBear250/crypto-teller-machine.git
cd crypto-teller-machine

# Start backend-api + kiosk-agent in simulator/testnet mode
podman-compose -f deploy/containers/compose.yaml up --build

# Check kiosk agent health
curl http://localhost:8080/health

# Check backend API health
curl http://localhost:8443/v1/health
```

---

## Architecture Summary

| Layer | OS | Role |
|-------|----|------|
| Kiosk terminal | **Fedora** (IoT / Workstation) | Touch UI, hardware abstraction (bill acceptor, QR scanner, cash dispenser, printer) |
| Backend services | **CentOS Stream 9** (RHEL ecosystem) | REST API, chain relay plugins, fleet management, audit storage |
| Communication | mTLS | Per-device certificates; kiosk initiates all connections (no inbound ports) |

See [`docs/architecture.md`](docs/architecture.md) for the full component diagram and
data flows.

---

## Supported Assets (Planned)

| Asset | Alpha | Beta | Notes |
|-------|:-----:|:----:|-------|
| LTC (Litecoin) | testnet | testnet → mainnet | Primary asset |
| DOGE (Dogecoin) | testnet | testnet → mainnet | |
| XRP | — | testnet | Destination tag required |
| SOL (Solana) | — | devnet | |

---

## Documentation

- [`docs/architecture.md`](docs/architecture.md) — Components, data flow, plugin model
- [`docs/deployment.md`](docs/deployment.md) — Fedora kiosk + CentOS backend setup
- [`docs/api.md`](docs/api.md) — REST API reference
- [`docs/security.md`](docs/security.md) — Security baseline and risk policy
- [`ROADMAP.md`](ROADMAP.md) — Alpha/Beta/Delta/Omega/Theta milestones

---

## License

MIT — see [`LICENSE`](LICENSE).
