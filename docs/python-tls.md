# Python TLS Implementation Guide

This document provides practical guidance for implementing the transport security policy defined in [`security-transport.md`](./security-transport.md) using Python.

---

## Recommended HTTP Libraries

Use one of the following libraries for all outbound HTTPS requests. Both default to verifying certificates.

| Library | Notes |
|---|---|
| [`httpx`](https://www.python-httpx.org/) | Modern, async-friendly, HTTP/1.1 + HTTP/2. Preferred for new code. |
| [`requests`](https://requests.readthedocs.io/) | Mature, synchronous, widely used. Acceptable for simpler use cases. |

**Never** disable verification:

```python
# BAD – never do this
requests.get(url, verify=False)
httpx.get(url, verify=False)
```

---

## Creating a Hardened SSLContext

For direct use of the `ssl` module (e.g., when wrapping sockets or configuring lower-level clients), create an `SSLContext` that enforces TLS ≥ 1.2 and enables hostname checking:

```python
import ssl

def create_tls_context() -> ssl.SSLContext:
    """Return an SSLContext enforcing TLS >= 1.2 with strict verification."""
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

    # Require TLS 1.2 as the minimum; TLS 1.3 is automatically available.
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2

    # Hostname checking and certificate verification are on by default
    # for PROTOCOL_TLS_CLIENT, but set them explicitly for clarity.
    ctx.check_hostname = True
    ctx.verify_mode = ssl.CERT_REQUIRED

    # Load the default system CA bundle.
    ctx.load_default_certs()

    return ctx
```

To add a client certificate for mTLS:

```python
ctx.load_cert_chain(certfile="/etc/ctm/device.crt", keyfile="/etc/ctm/device.key")
```

---

## Using the Context with `httpx`

```python
import httpx
import ssl

ctx = create_tls_context()

with httpx.Client(verify=ctx, timeout=httpx.Timeout(connect=5.0, read=15.0)) as client:
    response = client.get("https://backend.example.com/api/status")
    response.raise_for_status()
```

---

## Checking the Underlying TLS Library at Runtime

The CTM startup sequence should log which TLS library Python is using. This makes it easy to verify whether the deployment is running against OpenSSL or LibreSSL:

```python
import ssl

def log_tls_library() -> None:
    version = ssl.OPENSSL_VERSION  # e.g., "LibreSSL 3.8.2" or "OpenSSL 3.0.14 ..."
    print(f"TLS library: {version}")
    # In production, replace print() with your structured logger.
```

Call `log_tls_library()` during application startup, before any network connections are made, so it appears in every deployment's logs.

---

## Certificate Pinning

Certificate pinning ties a client to a specific certificate or CA and can reduce the risk of MITM attacks using a fraudulently issued certificate.

### Tradeoffs

| Approach | Operational complexity | Risk on cert rotation |
|---|---|---|
| **Pin leaf certificate** | High | High – client breaks if the server cert is renewed without a coordinated client update. |
| **Pin CA certificate** | Medium | Lower – client trusts any cert signed by the pinned CA; only breaks if the CA is replaced. |
| **No pinning (rely on system CAs)** | Low | None – standard WebPKI verification applies. |

**Recommendation:** If pinning is used, **pin the issuing CA** (not the leaf certificate). This avoids frequent client updates while still narrowing trust to a single CA. For the CTM use case, pinning the internal CA that issues device and backend certificates is a practical balance.

Example with `httpx` (pinning a custom CA):

```python
import httpx

with httpx.Client(verify="/etc/ctm/internal-ca.crt") as client:
    response = client.get("https://backend.example.com/api/status")
```

---

## Notes on LibreSSL and Python

As described in [`security-transport.md`](./security-transport.md#libressl-preference), Python's `ssl` module delegates to the TLS library it was compiled against. On Raspberry Pi OS / Debian this is typically OpenSSL.

The `ssl.OPENSSL_VERSION` string will show `"LibreSSL x.y.z"` if Python was built against LibreSSL. If you require LibreSSL specifically, the recommended path is to ship a controlled Python runtime (container or custom OS image) built against LibreSSL, rather than replacing the system OpenSSL.

The TLS policy (TLS ≥ 1.2, strict verification) applies the same way regardless of the underlying library.

---

*This document describes implementation guidance and does not constitute a compliance certification.*
