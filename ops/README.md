# Operations

This directory contains deployment, update, and monitoring configuration for the CTM.

## Contents (planned)

- `systemd/` — systemd unit files for the device daemon and kiosk UI.
- `provisioning/` — OS image hardening scripts and first-boot setup.
- `updates/` — over-the-air (OTA) update pipeline configuration.
- `monitoring/` — health check scripts and alerting rules.
- `backup/` — transaction log backup configuration.

## Deployment Plan

### OS Image

- Base: Raspberry Pi OS Lite (64-bit, Debian-based).
- Harden to kiosk mode:
  - Disable unused services (Bluetooth if not needed, unused USB ports via udev rules).
  - Auto-login to a dedicated `ctm` user (no sudo in normal operation).
  - Launch device daemon and kiosk UI via systemd on boot.
  - Prevent user access to desktop or shell through the display.
- Read-only root filesystem (OverlayFS) to reduce SD card wear and improve resilience.

### Service Management

- `ctm-device-daemon.service` — starts before `ctm-kiosk-ui.service`; restart on failure.
- `ctm-kiosk-ui.service` — starts Electron kiosk app; depends on device daemon socket being available.
- Both services use `Restart=on-failure` and `RestartSec=5`.

### Over-the-Air Updates

- Operator-triggered updates (no automatic updates without operator acknowledgment in production).
- Update package signed with operator key; signature verified before applying.
- Update process:
  1. Download and verify package.
  2. Drain any active transactions (or reject if machine busy).
  3. Apply update to a staging partition.
  4. Reboot; systemd brings up services; if health check fails, automatic rollback.

## Monitoring Plan

### Health Checks

The device daemon exposes a local health endpoint (HTTP on localhost only).  
A monitoring sidecar or remote probe checks:

- Daemon process alive.
- Last watchdog-pet timestamp within threshold.
- GPIO sensor last-read timestamp (detect stuck/dead sensor).
- Cash level (bills and tokens remaining).
- Network connectivity to backend services.

### Alerting

Alert operators on:

| Condition | Severity | Action |
|---|---|---|
| Daemon process down | Critical | Page on-call; machine goes out-of-service |
| Cash level low | Warning | Schedule cash reload |
| Token level low | Info | Schedule token reload |
| Dispenser fault | Critical | Machine out-of-service; investigate |
| Tamper event | Critical | Immediate alert; log with timestamp |
| Backend unreachable > 5 min | Warning | Monitor; transaction blocked until resolved |
| OTA update failed / rollback | Critical | Investigate before next update attempt |

### Log Shipping

- Transaction logs and fault logs shipped to operator-controlled remote storage.
- Logs must include: timestamp, transaction ID, state transitions, sensor readings at fault.
- Retain logs per applicable financial regulation in deployment jurisdiction.

## Status

This directory is a placeholder. Deployment scripts and monitoring configs will be added in Milestone M5.
