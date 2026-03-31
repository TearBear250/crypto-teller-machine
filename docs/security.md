# Security Baseline

## 1. Device Identity (mTLS)

Every kiosk is provisioned with a unique **device certificate** signed by the fleet
Certificate Authority (CA).

- Certificates are issued per-device with the kiosk ID in the `CN` field.
- The backend validates the device cert on every request (mutual TLS).
- Compromised or decommissioned kiosks are revoked via a CRL or OCSP responder.
- Certificates are stored in `/etc/ctm/tls/` with `0400` permissions, owned by the
  `ctm` service account.

**Rotation:** Device certificates should be rotated at least annually via the fleet-mgmt
service.

---

## 2. Network Security

### Kiosk (Fedora)

- **No inbound ports.** The kiosk firewall blocks all inbound connections.
- The kiosk-agent initiates all outbound HTTPS (port 8443) connections to the backend.
- `firewalld` zone: `drop` (default) with an explicit outbound-only rule for the backend IP.
- SELinux: **enforcing mode**; custom policy module for CTM services.

### Backend (CentOS Stream 9)

- Only ports 8443 (backend-api) and 8444 (fleet-mgmt) are exposed externally.
- All other services (chain-relay, PostgreSQL) are on an internal Podman network only.
- `firewalld` restricts inbound to those two ports; all other inbound is dropped.
- SELinux: **enforcing mode**.

---

## 3. Audit Logging

Every hardware and software event is logged **before** the corresponding action is taken.

- Logs are append-only; no deletion or modification is permitted by the CTM service account.
- The kiosk writes audit events to its local store AND posts them to the backend
  `POST /audit/events` endpoint.
- If the backend is unreachable, events are queued locally and flushed on reconnect.
- Audit log format is defined in `shared/schemas/audit-event.json`.

### Events logged (non-exhaustive)

| Category | Events |
|----------|--------|
| Cash | BILL_INSERTED, BILL_REJECTED, CASH_DISPENSED |
| Crypto | TX_BROADCAST, TX_CONFIRMED, TX_FAILED |
| Session | SESSION_CREATED, SESSION_CONFIRMED, SESSION_CANCELLED, SESSION_COMPLETED |
| Hardware | HAL_ERROR, DEVICE_RECONNECTED |
| Operator | OPERATOR_LOGIN, OPERATOR_LOGOUT, CONFIG_UPDATED |
| Security | CERT_ROTATION, POLICY_CHANGE, TAMPER_ALERT |

---

## 4. Confirmation and Risk Policy

**Cash-in (buy crypto):**

| Transaction Amount | Policy |
|-------------------|--------|
| ≤ CAD 50 | 1 confirmation minimum (0-conf is **not** recommended — RBF/double-spend risk) |
| CAD 51 – 500 | 2 confirmations |
| > CAD 500 | 3+ confirmations; operator alert |

**Cash-out (sell crypto):**

| Transaction Amount | Policy |
|-------------------|--------|
| ≤ CAD 50 | Chain-dependent minimum (e.g., 1 LTC conf) |
| CAD 51 – 200 | 2 confirmations minimum |
| > CAD 200 | 3+ confirmations; operator review recommended |

XRP and SOL settlements use finality indicators rather than confirmation counts:
- XRP: ledger closed + validated flag
- SOL: finalized slot

> **Note:** These are baseline policies for testnet/Alpha. Production risk parameters
> must be reviewed and adjusted before mainnet deployment.

---

## 5. Physical Security Considerations

- The kiosk cabinet should have a tamper-evident seal and intrusion detection switch.
- The HSM / secure element (if used for key material) should be wired to a tamper sensor
  that zeroizes keys on intrusion.
- The bill acceptor and cash cassette should be locked separately from the main cabinet.
- Camera / QR scanner should have a privacy shutter that closes when not in a scan step.

> These are design goals. Implementation of physical security hardware is outside the
> scope of this software repository.

---

## 6. Software Supply Chain

- All container images should be built from pinned base images with known SHA digests.
- Signed commits and signed container images (Sigstore / cosign) are targets for Beta.
- A Software Bill of Materials (SBOM) should be generated for each release.
- Dependency updates should be reviewed via automated CVE scanning before deployment.

---

## 7. Operator Access Controls

- Operator mode requires a **physical PIN + presence** at the machine (no remote
  operator login in Alpha).
- Operator sessions are logged (OPERATOR_LOGIN / OPERATOR_LOGOUT events).
- Operator cannot view or export user wallet addresses.
- Operator actions (e.g., cash fill, config change) require confirmation and are logged
  with a timestamp and operator ID.

---

## 8. Data Minimization

- The machine does **not** collect user identity information (non-custodial, non-KYC
  in testnet mode).
- Wallet addresses scanned by users are logged for audit trail but must be handled
  in accordance with applicable privacy regulations for production deployments.
- Session data older than the retention policy period should be purged from the backend
  database; audit logs are retained longer per compliance requirements.

---

## 9. Known Limitations (Alpha / Testnet)

- No production HSM integration yet; key material for backend signing uses software keys.
- No full CRL/OCSP revocation infrastructure yet; certificate rotation is manual in Alpha.
- Tamper-detection hardware integration is not implemented in this skeleton.
- Physical security interlocks (e.g., cabinet door sensor) are stubbed in the HAL.
- KYC / AML controls are out of scope for testnet; must be addressed before mainnet.
