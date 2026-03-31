# Deployment Guide

## Overview

This guide describes how to deploy:

- **Kiosk nodes** running **Fedora** (Fedora IoT or Fedora Workstation in kiosk mode)
- **Backend services** running **CentOS Stream 9** (RHEL ecosystem)

Both sides use **Podman** (rootless containers) managed by **systemd** for process
supervision. No Docker daemon is required.

---

## 1. Prerequisites

### Kiosk host (Fedora)

```bash
# Tested on Fedora 39+ (x86_64) and Fedora IoT 39+ (aarch64 / Raspberry Pi 5)
sudo dnf install -y podman podman-compose systemd

# Optional: enable Wayland kiosk mode (Cage compositor)
sudo dnf install -y cage
```

### Backend host (CentOS Stream 9)

```bash
# CentOS Stream 9 — RHEL ecosystem
sudo dnf install -y podman podman-compose systemd postgresql-server

# Enable PostgreSQL (if running natively; otherwise use the container)
sudo postgresql-setup --initdb
sudo systemctl enable --now postgresql
```

---

## 2. Architecture Summary

```
Fedora Kiosk                      CentOS Stream 9 Backend
─────────────                     ────────────────────────
kiosk-agent (Podman container)  ──►  backend-api (Podman container)
ltm-hal (host service / udev)        chain-relay (Podman container)
kiosk-ui (Podman container)          fleet-mgmt  (Podman container)
                                      PostgreSQL  (Podman container or native)
```

All kiosk → backend traffic uses **mTLS** (mutual TLS). The kiosk **never** accepts
inbound connections; it only initiates outbound calls to the backend.

---

## 3. Kiosk Deployment

### 3.1 Clone and configure

```bash
git clone https://github.com/TearBear250/crypto-teller-machine.git
cd crypto-teller-machine/kiosk

# Copy and edit environment file
cp .env.example .env
# Set: BACKEND_URL, KIOSK_ID, TLS_CERT_PATH, TLS_KEY_PATH, TLS_CA_PATH
```

### 3.2 Install systemd unit

```bash
# Copy unit file
sudo cp ../deploy/systemd/kiosk-agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now kiosk-agent.service
```

### 3.3 Verify

```bash
sudo systemctl status kiosk-agent.service
podman logs kiosk-agent
```

---

## 4. Backend Deployment

### 4.1 Clone and configure

```bash
git clone https://github.com/TearBear250/crypto-teller-machine.git
cd crypto-teller-machine/backend

cp .env.example .env
# Set: DB_URL, CHAIN_RPC_LTC, CHAIN_RPC_DOGE, CHAIN_RPC_XRP, CHAIN_RPC_SOL
#      TLS_CERT_PATH, TLS_KEY_PATH, TLS_CA_PATH
```

### 4.2 Start with podman-compose

```bash
cd deploy/containers
podman-compose up -d
```

This starts:
- `backend-api` on port 8443 (mTLS)
- `chain-relay` (internal only)
- `fleet-mgmt` on port 8444 (mTLS)
- `postgres` on internal network

### 4.3 Install systemd units

```bash
sudo cp ../deploy/systemd/backend-api.service /etc/systemd/system/
sudo cp ../deploy/systemd/chain-relay.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now backend-api.service chain-relay.service
```

---

## 5. TLS / mTLS Setup

Each kiosk has a unique device certificate signed by your internal CA.

```bash
# Generate CA (one time, on a secure machine)
openssl genrsa -out ca.key 4096
openssl req -new -x509 -key ca.key -out ca.crt -days 3650 \
  -subj "/CN=CTM-Internal-CA"

# Generate kiosk device cert
openssl genrsa -out kiosk-01.key 2048
openssl req -new -key kiosk-01.key -out kiosk-01.csr \
  -subj "/CN=kiosk-01/O=CTM-Fleet"
openssl x509 -req -in kiosk-01.csr -CA ca.crt -CAkey ca.key \
  -CAcreateserial -out kiosk-01.crt -days 365

# Distribute to kiosk
scp ca.crt kiosk-01.crt kiosk-01.key operator@kiosk-01:/etc/ctm/tls/
```

Set `TLS_CERT_PATH`, `TLS_KEY_PATH`, and `TLS_CA_PATH` in each `.env` accordingly.

---

## 6. Running Without Hardware (Development Mode)

Both the kiosk-agent and backend-api support a **simulator mode** for development on a
regular workstation, without any physical bill acceptor or cash dispenser attached.

```bash
# Kiosk simulator
cd kiosk
CTM_HAL_SIMULATE=true podman run --rm \
  --env-file .env \
  -e CTM_HAL_SIMULATE=true \
  -p 8080:8080 \
  localhost/ctm-kiosk-agent:dev

# Backend (testnet mode)
cd backend
CTM_CHAIN_TESTNET=true podman run --rm \
  --env-file .env \
  -e CTM_CHAIN_TESTNET=true \
  -p 8443:8443 \
  localhost/ctm-backend-api:dev
```

---

## 7. Podman Auto-Update (Recommended for Production)

```bash
# On both kiosk and backend hosts
sudo systemctl enable --now podman-auto-update.timer
```

Tag images with `io.containers.autoupdate=registry` to enable automatic rolling updates.

---

## 8. Recommended Hardware

| Role | Hardware |
|------|---------|
| Kiosk (primary) | x86_64 mini-PC with Fedora (≥ 8 GB RAM, 64 GB SSD) |
| Kiosk (Pi variant) | Raspberry Pi 5 (8 GB) with Fedora IoT (aarch64) |
| Backend | CentOS Stream 9 bare-metal or cloud VM (≥ 4 vCPU, 16 GB RAM, 100 GB SSD) |

---

## 9. Canada Testnet Region Notes

- All deployments in Canada (test region) should run against **testnets / devnets** only:
  - LTC: Litecoin testnet
  - DOGE: Dogecoin testnet
  - XRP: XRPL testnet (`testnet.xrpl-labs.com`)
  - SOL: Solana devnet
- Set `CTM_CHAIN_TESTNET=true` in environment to enforce testnet-only mode.
- Mainnet mode will be enabled in a later release after compliance review.

---

## 10. Next Steps

1. Implement chain plugin for LTC (testnet) — see `backend/chain-plugins/ltc/`.
2. Wire up a physical bill acceptor via `ltm-hal` MDB adapter.
3. Configure a real PostgreSQL instance with TimescaleDB for audit logs.
4. Set up monitoring (Prometheus + Grafana or equivalent) for the backend services.
