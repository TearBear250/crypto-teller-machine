# OpenPGP / GnuPG Signing Guide

This document describes how GnuPG (gpg) and the OpenPGP standard are used to sign and verify CTM release artifacts and software update bundles.

---

## Purpose

Using OpenPGP signatures on release artifacts serves two goals:

1. **Integrity** – Anyone (including the CTM device itself) can verify that an update bundle has not been tampered with after it was signed.
2. **Authenticity** – Signatures provide evidence that the artifact was created by a trusted party who holds the signing key.

---

## Signing Release Artifacts

### When to sign

Sign all artifacts that may be installed on a CTM device:

- OS image files (`.img`, `.img.gz`)
- Software update bundles (`.tar.gz`, `.zip`, or similar)
- Firmware packages
- Configuration files distributed through releases

### Signing a file

```bash
# Create a detached, ASCII-armored signature
gpg --batch --yes \
    --local-user "ctm-signing@example.com" \
    --armor \
    --detach-sign \
    update-bundle-v1.2.3.tar.gz
# Produces: update-bundle-v1.2.3.tar.gz.asc
```

Publish both the artifact and its `.asc` signature file together (e.g., as GitHub Release assets).

### Key ID / fingerprint in release notes

Include the full fingerprint of the signing key in release notes so that recipients can verify which key was used:

```
Signed with key: ABCD 1234 EFGH 5678 IJKL  9012 MNOP 3456 QRST 7890
```

---

## Verifying Signatures On-Device

Before installing an update bundle, the CTM device must verify the signature.

### Prerequisites on the device

The device must have the release team's **public key** imported into its GPG keyring:

```bash
# Import the public key (do this once during provisioning or via a secure update)
gpg --import ctm-release-public.asc
```

### Verification step

```bash
# Verify the detached signature before extracting/installing
gpg --verify update-bundle-v1.2.3.tar.gz.asc update-bundle-v1.2.3.tar.gz
```

The exit code of `gpg --verify` is `0` on success and non-zero on failure. The update installation script must check this exit code and abort if verification fails:

```bash
#!/usr/bin/env bash
set -euo pipefail

BUNDLE="update-bundle-v1.2.3.tar.gz"
SIG="${BUNDLE}.asc"

gpg --verify "$SIG" "$BUNDLE" || {
    echo "Signature verification FAILED. Aborting update." >&2
    exit 1
}

echo "Signature OK. Proceeding with installation."
# ... extract and apply the bundle
```

---

## Operational Guidance

### Keep the signing key offline

- The private signing key must **not** be stored on internet-connected build servers or CI runners.
- Keep the private key on an air-gapped machine, a hardware security key (e.g., YubiKey with OpenPGP support), or a hardware security module (HSM).
- For CI/CD pipelines that need to sign automatically, use a separate sub-key with limited capability, and revoke it if the CI environment is compromised.

### Key rotation

- Set an expiration date on signing keys (1–2 years is a reasonable interval).
- Before a key expires, generate a new key pair, sign the new public key with the old private key to establish continuity, and publish the new public key.
- After rotation, re-sign any artifacts that were signed with the old key if they are still being distributed.

### Publishing public keys

- Publish the current public signing key as a file in the repository (e.g., `keys/ctm-release-public.asc`) and as a GitHub Release asset.
- Include the full key fingerprint in `README.md` or a dedicated `KEYS` file so that users can verify the key out-of-band.

### Revocation

- Generate and securely store a **revocation certificate** for every key pair at the time of key creation.
- If a key is compromised, publish the revocation certificate immediately to a keyserver and update the repository's public key file.
- Notify all operators so they can update the key on their CTM devices.

---

## Key Management Summary

| Task | Who | When |
|---|---|---|
| Generate key pair | Release manager | Before first release |
| Store private key offline | Release manager | Always |
| Publish public key | Release manager | At key creation and after each rotation |
| Sign artifacts | Release manager / CI sub-key | On every release |
| Verify signature on-device | CTM update script | Before every update installation |
| Rotate key | Release manager | Before expiry or on compromise |

---

*This document describes operational guidance and does not constitute a compliance certification.*
