# Roadmap

This roadmap tracks the Alpha → Beta → Delta/Omega/Theta development plan for the
Crypto Teller Machine (CTM / LTM) platform.

**Test region:** Canada (testnet/devnet-first)  
**Production region:** North America (mainnet, post-Beta)

---

## Alpha — Cash-In on Testnets

**Goal:** A working end-to-end cash-in (buy crypto) flow on testnets, running on
Fedora kiosk hardware with a CentOS Stream 9 backend.

### Alpha Milestones

- [ ] Repository skeleton: `kiosk/`, `backend/`, `shared/`, `deploy/`, `docs/`
- [ ] OpenAPI contract (`shared/contracts/openapi.yaml`) stubbed
- [ ] JSON schemas for transactions, sessions, audit events
- [ ] `kiosk-agent` placeholder service (Fedora / Podman)
- [ ] `backend-api` placeholder service (CentOS / Podman)
- [ ] mTLS device certificate tooling
- [ ] `ltm-hal` simulator (bill acceptor + dispenser simulation without hardware)
- [ ] LTC plugin (Litecoin testnet) — end-to-end cash-in
- [ ] DOGE plugin (Dogecoin testnet) — end-to-end cash-in
- [ ] Basic kiosk UI (buy flow only, QR scan, receipt print)
- [ ] Audit logging to backend (append-only)
- [ ] Operator console (cash levels, session list, logs)
- [ ] Systemd + Podman deployment on Fedora (x86_64) validated
- [ ] Systemd + Podman deployment on Fedora IoT (aarch64 / Pi 5) validated
- [ ] Canada testnet deployment guide published

---

## Beta — Add Cash-Out + More Assets

**Goal:** Full buy/sell flows, expanded asset support, and hardened deployment.

### Beta Milestones

- [ ] Cash-out (sell crypto → cash dispense) flow complete
- [ ] Per-chain confirmation / risk policy engine
- [ ] XRP plugin (XRPL testnet) — cash-in + cash-out with destination-tag UX
- [ ] SOL plugin (Solana devnet) — cash-in + cash-out
- [ ] Multi-kiosk fleet management (device registration, config push, health monitoring)
- [ ] Podman auto-update pipeline (signed images)
- [ ] SBOM generation for all container images
- [ ] Rate limiting + daily/per-session limits configurable per kiosk
- [ ] Prometheus metrics + Grafana dashboard for backend
- [ ] Physical bill acceptor integration (MDB protocol adapter in `ltm-hal`)
- [ ] Physical cash dispenser integration (`ltm-hal`)
- [ ] End-to-end test suite (hardware simulator)
- [ ] Security hardening review (SELinux policies, firewall rules)
- [ ] Canada testnet → Canada mainnet readiness assessment

---

## Delta — Multi-Asset Expansion and Paper Instruments

**Goal:** Expand the asset menu, introduce paper wallet receipts (optional, with HSM).

### Delta Milestones

- [ ] BNB / additional asset plugins (community contributions welcome)
- [ ] Paper wallet receipts with secure key generation (HSM integration path)
- [ ] Receipt printer integration (`ltm-hal` printer adapter)
- [ ] Multi-language UI support
- [ ] Per-machine fee schedule configuration
- [ ] Remote operator console (fleet-level dashboard)
- [ ] Tamper-detection hardware integration (`ltm-hal` intrusion sensor adapter)
- [ ] Signed release process (Sigstore / cosign)

---

## Omega — Production Readiness

**Goal:** Production mainnet deployments in Canada; compliance-ready.

### Omega Milestones

- [ ] KYC / AML policy engine (pluggable; operator-configurable per jurisdiction)
- [ ] CRL / OCSP infrastructure for device certificate revocation
- [ ] Hardware security module (HSM) integration for backend signing keys
- [ ] Reproducible builds for all container images
- [ ] Third-party security audit
- [ ] Mainnet deployment: Canada
- [ ] Operator training materials

---

## Theta — North American Expansion

**Goal:** Expand beyond Canada; community operator model.

### Theta Milestones

- [ ] US regulatory compliance review (FinCEN MSB requirements)
- [ ] Per-jurisdiction compliance plugin interface
- [ ] Satellite / alternative transport provider integration
- [ ] Operator franchise / white-label deployment guide
- [ ] Community plugin SDK documentation
- [ ] Mainnet deployment: United States (select states)

---

## Asset Support Matrix

| Asset | Alpha (testnet) | Beta (testnet) | Delta | Omega (mainnet) |
|-------|:-:|:-:|:-:|:-:|
| LTC   | ✓ planned | ✓ | ✓ | ✓ |
| DOGE  | ✓ planned | ✓ | ✓ | ✓ |
| XRP   | — | ✓ planned | ✓ | ✓ |
| SOL   | — | ✓ planned | ✓ | ✓ |
| BNB   | — | — | ✓ planned | ✓ |

---

## Contributing

See `CONTRIBUTING.md` (to be added). Plugin contributions (new chain adapters) are
especially welcome — follow the `ChainPlugin` interface in `shared/schemas/`.
