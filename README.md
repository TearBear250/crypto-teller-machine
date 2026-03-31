# crypto-teller-machine
The the OS for the crypto teller machine crypto telling machines will have a likes of a few safety protocols built into prevent people from committing fraud against the blockchain of altcoins and crypto coins from across the internet but then also a fail safe for those who want to use counterfeit $20 bills to try to buy things from us. 

## Security

All CTM network communication uses TLS 1.2/1.3 with strict certificate validation. Software update bundles are signed with OpenPGP (GnuPG) and verified on-device before installation.

| Document | Description |
|---|---|
| [`docs/security-transport.md`](docs/security-transport.md) | Transport security requirements: TLS policy, certificate validation, mTLS, LibreSSL preference, and threat model. |
| [`docs/python-tls.md`](docs/python-tls.md) | Python implementation guidance: recommended libraries, hardened SSLContext, runtime TLS library inspection, and certificate pinning tradeoffs. |
| [`docs/pgp-signing.md`](docs/pgp-signing.md) | OpenPGP/GnuPG guidance: signing release artifacts, on-device verification, key rotation and revocation. |

