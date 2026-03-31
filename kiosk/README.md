# Kiosk Service (Fedora)

This directory contains the **kiosk-agent** — the on-device service that runs on
**Fedora** (x86_64 or aarch64 / Raspberry Pi 5) inside the CTM/LTM kiosk cabinet.

## Components

| Component | Description |
|-----------|-------------|
| `kiosk-agent/` | Transaction state machine; talks to backend-api over mTLS |
| `ltm-hal/` | Hardware Abstraction Layer (bill acceptor, cash dispenser, QR scanner, receipt printer) |
| `kiosk-ui/` | Full-screen Wayland/X11 touch UI |

## Prerequisites

- Fedora 39+ (x86_64) **or** Fedora IoT 39+ (aarch64)
- Podman ≥ 4.x
- `podman-compose` (optional, for multi-service local dev)
- `systemd` (standard on Fedora)

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
| `BACKEND_URL` | Base URL of the backend-api (e.g. `https://backend.ctm.internal:8443/v1`) |
| `KIOSK_ID` | Unique kiosk identifier (e.g. `kiosk-ca-001`) |
| `TLS_CERT_PATH` | Path to device TLS certificate |
| `TLS_KEY_PATH` | Path to device TLS private key |
| `TLS_CA_PATH` | Path to fleet CA certificate |
| `CTM_HAL_SIMULATE` | Set to `true` to simulate hardware (no physical devices needed) |
| `CTM_CHAIN_TESTNET` | Set to `true` to enforce testnet-only mode |
| `LOG_LEVEL` | `debug`, `info`, `warn`, or `error` |

## Running Locally (Simulator Mode)

No hardware required. The HAL simulator emulates bill insertion and cash dispensing.

```bash
# Build the kiosk-agent image
podman build -t localhost/ctm-kiosk-agent:dev -f ../deploy/containers/Containerfile.kiosk .

# Run in simulator mode
podman run --rm \
  --env-file .env \
  -e CTM_HAL_SIMULATE=true \
  -e CTM_CHAIN_TESTNET=true \
  -p 8080:8080 \
  localhost/ctm-kiosk-agent:dev
```

The agent exposes a local HTTP health endpoint at `http://localhost:8080/health`.

## Running with systemd (Production)

```bash
# Install and enable the systemd unit
sudo cp ../deploy/systemd/kiosk-agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now kiosk-agent.service

# Check status
sudo systemctl status kiosk-agent.service
podman logs kiosk-agent
```

## Directory Structure

```
kiosk/
├── README.md              # This file
├── .env.example           # Environment variable template
├── kiosk-agent/           # Agent service placeholder
│   └── main.py            # Hello-service entrypoint (placeholder)
├── ltm-hal/               # Hardware Abstraction Layer
│   └── simulator.py       # HAL simulator for development
└── kiosk-ui/              # Kiosk touch UI (future)
```

## Next Steps

1. Implement `kiosk-agent/main.py` with full session state machine.
2. Implement `ltm-hal/` adapters for physical devices (MDB bill acceptor, cash dispenser).
3. Build out `kiosk-ui/` with buy/sell touch flows.
4. Wire up mTLS using the device certificate from `docs/deployment.md`.
