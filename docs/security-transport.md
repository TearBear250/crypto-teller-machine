# Transport Security Requirements

This document defines the transport security requirements for the Crypto Teller Machine (CTM) software. All network communication from a CTM device must meet these requirements.

---

## TLS Protocol Version Policy

- **TLS 1.2 and TLS 1.3 are the only permitted protocol versions.**
- SSL 2.0, SSL 3.0, TLS 1.0, and TLS 1.1 **must be disabled** at the application level.
- The CTM software must explicitly configure its TLS context to enforce this floor rather than relying on system defaults.

## Certificate Validation

- **Full chain validation is required.** The CTM must verify the server certificate against a trusted CA bundle.
- **Hostname verification is required.** The presented certificate's subject/SAN must match the hostname being contacted.
- Self-signed certificates are not permitted for production endpoints.
- Certificate verification must never be disabled (e.g., no `verify=False`, no `ssl.CERT_NONE`).

## Cipher Suites

- Prefer cipher suites supporting forward secrecy (ECDHE/DHE key exchange).
- Disable NULL, EXPORT, RC4, DES, and 3DES cipher suites.
- Rely on the TLS library's secure defaults for TLS 1.3 (which mandates strong suites).

## Mutual TLS (mTLS) for Device Identity

Each deployed CTM unit should have a unique device certificate issued by an internal certificate authority (CA). The backend API should require and validate the client certificate on every request (mutual TLS / mTLS).

High-level approach:

1. An internal CA issues a device certificate per CTM (e.g., `ctm-unit-<serial>.crt`).
2. The CTM's private key is stored with restricted filesystem permissions; ideally protected by a hardware secure element.
3. The backend validates the client certificate chain and checks the device serial against an allowlist.
4. Revoked device certificates are refused immediately (via OCSP or a CRL endpoint, or a simple allowlist check).

mTLS is strongly recommended because it provides device-level authentication without relying solely on shared API keys or tokens.

## Certificate Provisioning, Rotation, and Revocation

- Certificates must have a defined expiration period (90–365 days recommended).
- A certificate rotation procedure must exist and be tested before a cert expires.
- Expired or compromised device certificates must be added to a revocation list and the backend must enforce that list.
- Root and intermediate CA private keys must be kept offline or in an HSM.

## Timeouts and Retries

- All outbound HTTP(S) requests must have explicit timeouts (connect timeout and read timeout).
- Do not retry on authentication/authorization failures (4xx); only retry on transient network errors or 5xx with exponential back-off and jitter.
- A maximum retry count must be enforced.

## No Plaintext Admin Endpoints

- Administrative endpoints must not be accessible over plain HTTP.
- Remote shell/admin access should be tunneled through a VPN (e.g., WireGuard) or protected by mTLS—never exposed directly to the internet.
- Local admin ports (e.g., on `127.0.0.1`) must be firewalled from external interfaces.

## Logging Guidance

To prevent credential leakage in logs:

- **Never log** API keys, passwords, tokens, private key material, or other secrets.
- **Avoid logging full URLs** that contain authentication tokens in query parameters. Strip or redact tokens before logging.
- Log connection errors and TLS handshake failures at an appropriate level (e.g., `ERROR`) without including sensitive header values.
- Structured logging is preferred; include fields such as `host`, `status_code`, `duration_ms`, and `request_id` rather than raw request/response bodies.

---

## LibreSSL Preference

### Background

In Python, TLS functionality comes from the built-in `ssl` module, which is a thin wrapper around the TLS library that Python was compiled against. On Debian-based systems (including Raspberry Pi OS), this is almost always **OpenSSL**. LibreSSL is the default TLS library on OpenBSD and macOS, but it is not the default on Raspberry Pi OS.

### What the repo can and cannot control

- **Policy** (minimum TLS version, certificate validation, cipher preferences) can be enforced in application code regardless of whether the underlying library is OpenSSL or LibreSSL. This is the highest-impact control and should be implemented first.
- **Library selection** is determined by how Python itself was compiled. Changing the system-wide TLS library on Raspberry Pi OS is complex and risky; it can break `apt`, `curl`, and many system tools that depend on the OpenSSL ABI.

### Options if strict LibreSSL is required

1. **Build Python against LibreSSL** – Compile CPython from source with `--with-openssl` pointing to a LibreSSL installation. This Python binary must then be used exclusively for CTM software, isolated from the system Python.

2. **Ship a controlled runtime** – Package the CTM software in a container image (Docker/OCI) or a reproducible OS image (e.g., a custom Raspberry Pi OS build or Buildroot image) that includes a Python runtime linked to LibreSSL. This is the cleanest approach and avoids conflict with the host OS.

3. **Accept OpenSSL underneath** – Enforce the TLS policy (TLS ≥ 1.2, strict verification, strong ciphers) at the application layer. The functional security outcome is equivalent to LibreSSL for typical deployments. Document this decision as an accepted trade-off.

Replacing the OS-wide OpenSSL on Raspberry Pi OS/Debian is **not recommended** because it will likely break system package management and other OS components.

### Runtime library check

The CTM startup sequence should log which TLS library Python is using so that compliance checks can be automated:

```python
import ssl
print(ssl.OPENSSL_VERSION)  # e.g., "LibreSSL 3.8.2" or "OpenSSL 3.0.x ..."
```

---

## Threat Model Notes

The CTM operates on public or semi-public networks (retail floors, kiosks, etc.). The following threats are in scope:

| Threat | Mitigation |
|---|---|
| **Public network / untrusted Wi-Fi** | TLS 1.2/1.3 with full certificate validation; prefer mTLS for device-to-backend traffic. |
| **Man-in-the-Middle (MITM)** | Hostname verification + CA pinning; mTLS so the server also authenticates the device. |
| **Stolen or tampered device** | Device certificate revocation; encrypted storage for keys; tamper detection in hardware design. |
| **Replay / credential theft** | Short-lived tokens; never log tokens; rotate device certs regularly. |

---

*This document describes requirements and design intent. It does not constitute a compliance certification.*
