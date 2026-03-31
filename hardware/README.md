# Hardware

This directory collects bill-of-materials (BOM), enclosure design notes, and hardware integration references for the CTM.

## Contents (planned)

- `BOM.csv` — component list with part numbers, suppliers, and quantities.
- `enclosure/` — CAD files or dimensional drawings for the CTM cabinet.
- `wiring/` — wiring diagrams, GPIO signal maps, and power rail schematics.
- `datasheets/` — key component datasheets (add as PDFs or links in a markdown index).

## Design Principles

All hardware design must comply with:

- [`docs/safety.md`](../docs/safety.md) — physical safety requirements (entanglement, pinch points, interlocks).
- [`docs/gpio-safety.md`](../docs/gpio-safety.md) — Raspberry Pi GPIO safety and driver requirements.

## Component Categories (notes placeholder)

### Compute

- Raspberry Pi (model TBD — Pi 4B or Pi 5 recommended for GPIO + display + USB).
- MicroSD card (32 GB+ Class 10 / A2 rated).

### Display and Input

- Official Raspberry Pi touch display or compatible 7–10" HDMI touchscreen.
- Optional: barcode/QR scanner (USB HID keyboard emulation type).

### Cash Handling

- **Bill acceptor** — must support ccTalk, MDB, or documented USB-serial protocol on Linux.
- **Bill dispenser** — must support ccTalk, MDB, or documented serial protocol on Linux.
- Avoid models requiring proprietary Windows-only vendor SDKs.

### Printer

- **Receipt printer** — ESC/POS compatible USB or serial. Widely supported on Linux.

### Drawer Mechanism

- Electromechanical latch/lock (solenoid or motor latch) — to be selected.
- Drawer-closed microswitch (normally-closed, rated for 100k+ cycles).
- Tamper switch for service door (normally-closed).
- Optional: cash-present optical or IR sensor in pocket.

### Souvenir Token Dispenser (optional)

- Standard coin/token hopper dispenser — sized for selected token diameter.
- See [`docs/token-dispenser.md`](../docs/token-dispenser.md) for token dimension requirements.

### Power

- Mains power supply: regulated DC outputs for Pi (5V) and actuators (12V or 24V — TBD by actuator spec).
- UPS/battery backup (recommended for clean shutdown on mains loss).

## Status

This directory is a placeholder. BOM and drawings will be added in Milestone M1.
