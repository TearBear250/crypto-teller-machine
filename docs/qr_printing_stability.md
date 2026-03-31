# QR Code and Printing Stability Guide

This document defines the **canonical QR payload rules**, quiet-zone and
error-correction guidance, and template versioning rules that keep all kiosks
printing identical, scannable vouchers.

---

## Canonical QR Payload Rules

Every QR code printed by a CTM/LTM kiosk encodes a **URI** of the form:

```
ctm://claim/<opaque-token>
```

### Rules

| Rule | Requirement |
|------|-------------|
| **Prefix is fixed** | Always `ctm://claim/` (from `QrProfile.uri_prefix`). Never embed denomination, amount, or address in the URI. |
| **Token is opaque** | The token is a URL-safe random string (e.g., UUID v4 without dashes). No structured data inside the token. |
| **No query parameters** | The kiosk appends only the token. Never add `?amount=` or similar. Amounts are printed as human-readable text, not encoded in the QR. |
| **Denomination ID in separate field** | The denomination ID (e.g., `COIN_USD_025`) is printed as a text field on the voucher. It is never embedded in the QR URI. |
| **Blockchain addresses are separate** | If a paper wallet address is printed, it gets its own QR code. The claim URI QR and the wallet address QR are never combined. |
| **UTF-8, no binary** | QR payload is pure ASCII/UTF-8. No binary or Shift-JIS encoding modes. |

### Why a claim URI instead of encoding the address directly?

Encoding a raw blockchain address in a QR code is tempting but causes problems:

- Different address formats (legacy, bech32, EIP-55 checksums) produce
  different QR data for the same key, making scan validation fragile.
- A voucher that encodes the private key directly is a security liability if
  the voucher is photographed.
- A claim-token flow lets the backend verify the voucher is genuine and
  unspent before revealing the wallet credentials to the companion phone app.

---

## Quiet Zone Requirements

The QR specification (ISO/IEC 18004) requires a **quiet zone** of at least
4 modules (the empty white border) around the symbol.  On a thermal printer
with small DPI, crowding the QR to the edge of the paper often causes the
quiet zone to be clipped, making the code unscannable.

### Minimum values (enforced by `QrProfile`)

| Field                 | Minimum | Recommended |
|-----------------------|---------|-------------|
| `quiet_zone_modules`  | 4       | 6           |
| `module_size_mm`      | 0.25 mm | 0.5 mm      |

**Calculation — QR code physical width:**

```
total_modules = qr_version_modules + (2 × quiet_zone_modules)
physical_width_mm = total_modules × module_size_mm
```

For a Version 3 QR (29×29 modules) with 6 quiet-zone modules at 0.5 mm:

```
(29 + 12) × 0.5 mm = 20.5 mm
```

This fits comfortably on 80 mm receipt paper and leaves room for the text fields.

### Guidance for different paper widths

| Paper       | Min module size | Quiet zone | Notes |
|-------------|-----------------|------------|-------|
| receipt_80mm | 0.5 mm         | 6 modules  | Standard; fits QR + text beside it |
| receipt_58mm | 0.4 mm         | 4 modules  | Minimum; avoid if possible |
| a6          | 0.75 mm         | 6 modules  | Higher quality, easier scan |

---

## Error Correction Guidance

| Level | Recovery capacity | Use when |
|-------|------------------|----------|
| L     | ~7%  | Never use for printed vouchers — any smudge causes failure |
| M     | ~15% | **Minimum** for receipt paper; handles minor wear |
| Q     | ~25% | **Recommended default**; handles fold marks and light stains |
| H     | ~30% | High-wear environments (outdoor kiosks, humid climates) |

The `QrProfile.error_correction` field controls which level all kiosks use.
Changing this field fleet-wide requires bumping `KioskConfig.spec_version`.

> **Rule:** Never go below `M`.  A voucher that cannot be scanned is a
> financial loss.  Use `Q` as the default.

---

## Template Versioning

Every printed voucher is produced by a named **template** identified by
`PrintProfile.template_id` and `PrintProfile.template_version`.

### Why template versioning matters

If kiosks can each evolve their print templates independently:

- QR position shifts → scanners miss the quiet zone → failed scans.
- Font size changes → denomination text truncated → customer confusion.
- Paper margin differences → vouchers fold on critical content.

By pinning `template_id` + `template_version` in the fleet config, the
backend ensures every kiosk in the fleet prints an **identical** physical
voucher.

### Template version format

```
MAJOR.MINOR.PATCH  (semantic versioning)
```

| Change type | Version bump | Example |
|-------------|-------------|---------|
| QR position, size, quiet zone | MAJOR | 1.0.0 → 2.0.0 |
| Text field layout or font size | MINOR | 1.0.0 → 1.1.0 |
| Typo fix, color tweak | PATCH | 1.0.0 → 1.0.1 |

### Kiosk behavior on template mismatch

If a kiosk receives a `PrintProfile` with a `template_version` it does not
have loaded locally, it **must**:

1. Refuse to print (do not print with the wrong template).
2. Log a `CONFIG_MISMATCH` audit event with metadata:
   - `required_template_id`
   - `required_template_version`
   - `available_template_versions` (array)
3. Display an operator alert: "Print template update required."
4. Continue accepting cash and crypto transactions (sessions can still
   complete); only printing is blocked.

### Deploying a new template

1. Build and test the new template locally.
2. Assign the new `template_version` string.
3. Distribute the template package to all kiosk units (via OTA or manual).
4. Once all kiosks confirm receipt (via heartbeat `software_version` or a
   dedicated template-ack endpoint), update `PrintProfile.template_version`
   in the fleet config.
5. Kiosks pick up the new version on their next `/fleet/config` poll and
   resume printing.

**Never** push a new `template_version` to `/fleet/config` before the
template package has been distributed.  Doing so will block printing on all
kiosks that have not yet received the package.

---

## QrProfile and PrintProfile in KioskConfig

Both profiles are delivered via the `/fleet/config` endpoint as part of
`KioskConfig`.  Example payload fragment:

```json
{
  "spec_version": "2026-03-31.1",
  "qr_profile": {
    "format": "uri",
    "uri_prefix": "ctm://claim/",
    "error_correction": "Q",
    "module_size_mm": 0.5,
    "quiet_zone_modules": 6
  },
  "print_profile": {
    "paper": "receipt_80mm",
    "dpi": 203,
    "template_id": "voucher_v1",
    "template_version": "1.0.0"
  }
}
```

Kiosks must validate both objects against the schemas in
`shared/schemas/qr_profile.schema.json` and
`shared/schemas/print_profile.schema.json` before applying them.
