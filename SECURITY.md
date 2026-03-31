# Security Policy

## Reporting a Vulnerability

> **Please do NOT open a public GitHub issue to report a security vulnerability.**

The CTM handles physical cash, cryptocurrency transactions, and physical safety systems (interlocks, actuators).  
A security vulnerability in this project could have consequences beyond software — including financial loss, physical safety hazards, or fraud.  
We take all security reports seriously.

### How to Report

Send a detailed report to the project maintainers by one of these methods:

1. **GitHub private vulnerability reporting** — use the "Report a vulnerability" button on the [Security tab](../../security/advisories/new) of this repository (preferred).
2. **Email** — if private GitHub reporting is not available, contact the repository owner directly via the email address listed on their GitHub profile.

### What to Include in Your Report

Please provide as much of the following as you can:

- A description of the vulnerability and where it exists (file, component, protocol).
- Steps to reproduce or a proof-of-concept.
- The potential impact (e.g., unauthorized cash dispense, remote code execution, interlock bypass, physical safety risk).
- Any suggested mitigations you are aware of.

### Response Timeline

| Action | Target time |
|---|---|
| Acknowledge receipt of report | Within 3 business days |
| Confirm or dispute vulnerability | Within 10 business days |
| Patch or mitigation plan communicated | Within 30 days (critical issues sooner) |

We will credit reporters in the release notes unless they request anonymity.

---

## Supported Versions

This project is in early development (scaffold / pre-release). There are no versioned releases yet.  
Once releases are published, this section will list which versions receive security fixes.

| Version | Supported |
|---|---|
| Pre-release (main branch) | ✅ |

---

## Special Considerations for This Project

The CTM is not just a software project. Please consider the following when reporting:

### Physical Safety

Vulnerabilities that could cause a physical safety hazard — such as bypassing interlocks that prevent actuators from running while the drawer is open — are treated as **critical severity** regardless of the complexity of exploitation. Report these immediately.

### Financial and Cash Handling

Vulnerabilities that could result in unauthorized cash dispensing, incorrect transaction recording, or manipulation of exchange rates are treated as **critical severity**.

### GPIO and Hardware

Vulnerabilities that could drive GPIO outputs to unsafe states (e.g., enabling a motor driver without proper interlock confirmation) are treated as **critical severity**.

### Cryptocurrency / Wallet

Vulnerabilities related to private key exposure, wallet address substitution (address-swapping attacks), or transaction manipulation are treated as **critical severity**.

---

## Out of Scope

The following are generally out of scope for this security policy:

- Vulnerabilities in third-party dependencies (report those to the relevant upstream project).
- Physical attacks requiring unrestricted physical access to the interior of a locked enclosure (these are physical security concerns, not software security vulnerabilities — though we still welcome notes on enclosure hardening).
- Social engineering attacks against operators.

---

## Disclosure Policy

We follow **coordinated disclosure**: we ask that reporters give us reasonable time to fix a vulnerability before public disclosure. We aim to work collaboratively with reporters and will communicate progress throughout the fix cycle.
