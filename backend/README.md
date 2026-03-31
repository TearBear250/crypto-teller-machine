# Backend Service (CentOS Stream 9)

This directory contains the **backend-api** and associated chain plugins that run on
**CentOS Stream 9** (RHEL ecosystem) on the server farm.

## Components

| Component | Description |
|-----------|-------------|
| `backend-api/` | REST API service (implements `shared/contracts/openapi.yaml`) |
| `chain-plugins/` | Pluggable chain connectors (LTC, DOGE, XRP, SOL) |

## Prerequisites

- CentOS Stream 9 (or Rocky Linux 9 / AlmaLinux 9)
- Podman ≥ 4.x
- `podman-compose`
- PostgreSQL 15+ (or use the bundled container)

```bash
sudo dnf install -y podman podman-compose
```

## Environment Variables

Copy `.env.example` to `.env` and fill in the required values:

```bash
cp .env.example .env
```

| Variable | Description |
|----------|-------------|
| `DB_URL` | PostgreSQL connection string |
| `TLS_CERT_PATH` | Path to server TLS certificate |
| `TLS_KEY_PATH` | Path to server TLS private key |
| `TLS_CA_PATH` | Path to fleet CA certificate (for verifying kiosk device certs) |
| `CHAIN_RPC_LTC` | Litecoin RPC endpoint (testnet or mainnet) |
| `CHAIN_RPC_DOGE` | Dogecoin RPC endpoint |
| `CHAIN_RPC_XRP` | XRP Ledger WebSocket endpoint |
| `CHAIN_RPC_SOL` | Solana JSON-RPC endpoint |
| `CTM_CHAIN_TESTNET` | Set to `true` to enforce testnet-only mode |
| `LOG_LEVEL` | `debug`, `info`, `warn`, or `error` |

## Running Locally (Development Mode)

No chain nodes or real database required in development mode. The service stubs respond
with placeholder data.

```bash
# Build the backend-api image
podman build -t localhost/ctm-backend-api:dev -f ../deploy/containers/Containerfile.backend .

# Run in development mode (no real DB or chain nodes)
podman run --rm \
  --env-file .env \
  -e CTM_CHAIN_TESTNET=true \
  -p 8443:8443 \
  localhost/ctm-backend-api:dev
```

The service exposes a health endpoint at `https://localhost:8443/v1/health`.

## Running with podman-compose

```bash
cd ../deploy/containers
podman-compose up -d
```

This starts:
- `backend-api` (port 8443)
- `chain-relay` (internal)
- `fleet-mgmt` (port 8444)
- `postgres` (internal)

## Running with systemd (Production)

```bash
sudo cp ../deploy/systemd/backend-api.service /etc/systemd/system/
sudo cp ../deploy/systemd/chain-relay.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now backend-api.service chain-relay.service
```

## Directory Structure

```
backend/
├── README.md                  # This file
├── .env.example               # Environment variable template
├── backend-api/               # API service placeholder
│   └── main.py                # Hello-service entrypoint (placeholder)
└── chain-plugins/             # Chain connector plugins
    ├── ltc/                   # Litecoin plugin (placeholder)
    ├── doge/                  # Dogecoin plugin (placeholder)
    ├── xrp/                   # XRP plugin (placeholder)
    └── sol/                   # Solana plugin (placeholder)
```

## Chain Plugin Interface

Each chain plugin must implement the following interface (to be enforced by the
chain-relay service):

```python
class ChainPlugin:
    def validate_address(self, address: str) -> dict:
        """Returns { ok: bool, normalized: str, warnings: list }"""

    def get_quote(self, fiat_amount: float, fiat_currency: str) -> dict:
        """Returns { asset_amount: float, rate: float, fee_fiat: float }"""

    def build_payout_tx(self, destination: str, amount: float) -> dict:
        """Returns a serialized transaction ready to broadcast"""

    def broadcast_tx(self, tx: dict) -> str:
        """Broadcasts tx and returns txid"""

    def track_tx(self, txid: str) -> dict:
        """Returns { state, confirmations, block_height }"""

    def required_confirmations(self, fiat_amount: float) -> int:
        """Returns minimum confirmations for the given fiat amount"""
```

See `shared/schemas/` for JSON schemas used by these plugins.

## Next Steps

1. Implement `backend-api/main.py` with full OpenAPI-compliant REST handlers.
2. Implement `chain-plugins/ltc/` for Litecoin testnet.
3. Set up PostgreSQL schema (migrations to be added to `backend/migrations/`).
4. Wire up mTLS verification of kiosk device certificates.
