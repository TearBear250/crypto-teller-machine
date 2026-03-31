# Deploy — Containers & systemd

This directory contains everything needed to build and run the CTM/LTM services
using **Podman** (rootless) managed by **systemd**.

---

## containers/

| File | Description |
|------|-------------|
| `Containerfile.kiosk` | Container image for `ctm-kiosk-agent` — based on **Fedora 39** |
| `Containerfile.backend` | Container image for `ctm-backend-api` — based on **CentOS Stream 9** |
| `compose.yaml` | podman-compose file for local development (all services) |

### Build images locally

```bash
# From repo root
podman build -t localhost/ctm-kiosk-agent:dev \
  -f deploy/containers/Containerfile.kiosk .

podman build -t localhost/ctm-backend-api:dev \
  -f deploy/containers/Containerfile.backend .
```

### Run with podman-compose (development)

```bash
podman-compose -f deploy/containers/compose.yaml up --build
```

### Multi-arch builds (x86_64 + aarch64 for Raspberry Pi 5)

```bash
# Requires podman with buildx / qemu-user-static
podman build --platform linux/amd64,linux/arm64 \
  -t registry.example.com/ctm-kiosk-agent:latest \
  -f deploy/containers/Containerfile.kiosk .
```

---

## systemd/

| File | Description |
|------|-------------|
| `kiosk-agent.service` | Systemd unit for kiosk-agent on **Fedora** |
| `backend-api.service` | Systemd unit for backend-api on **CentOS Stream 9** |
| `chain-relay.service` | Systemd unit for chain-relay on **CentOS Stream 9** |

### Install on Fedora (kiosk)

```bash
# Create service user
sudo useradd --system --no-create-home ctm-agent

# Copy environment file
sudo mkdir -p /etc/ctm
sudo cp kiosk/.env.example /etc/ctm/kiosk-agent.env
sudo chmod 600 /etc/ctm/kiosk-agent.env

# Install and start
sudo cp deploy/systemd/kiosk-agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now kiosk-agent.service
sudo systemctl status kiosk-agent.service
```

### Install on CentOS Stream 9 (backend)

```bash
# Create service user
sudo useradd --system --no-create-home ctm-api

# Copy environment files
sudo mkdir -p /etc/ctm
sudo cp backend/.env.example /etc/ctm/backend-api.env
sudo chmod 600 /etc/ctm/backend-api.env

# Install and start backend-api
sudo cp deploy/systemd/backend-api.service /etc/systemd/system/
sudo cp deploy/systemd/chain-relay.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now backend-api.service chain-relay.service
sudo systemctl status backend-api.service chain-relay.service
```

### Enable Podman auto-update (recommended for production)

```bash
sudo systemctl enable --now podman-auto-update.timer
```

Images tagged with `io.containers.autoupdate=registry` will be updated automatically.

---

## Notes

- All services run **rootless** (non-root user accounts `ctm-agent` / `ctm-api`).
- TLS certificates live in `/etc/ctm/tls/`; see `docs/deployment.md` for CA setup.
- Logs go to `journald`; view with `journalctl -u kiosk-agent -f`.
- SELinux must be in **enforcing** mode on both Fedora and CentOS.
