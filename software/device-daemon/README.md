# Device Daemon

Placeholder for the CTM Device Daemon service.

## Responsibility

The Device Daemon is a background service running on the Raspberry Pi.  
It is the **sole** owner of all GPIO access and hardware control for the CTM.

### Core functions

- **GPIO monitoring** — polls or receives interrupts from all digital inputs:
  - Drawer closed/open switches.
  - Tamper switch on service door.
  - Cash-present sensor in drawer pocket.
  - Dispenser fault signal.
- **Interlock enforcement** — hardware-level and software-level interlocks (see `docs/safety.md`):
  - Drawer must be confirmed closed before dispenser enable.
  - Stop all actuators immediately on drawer-open or tamper event.
- **Actuator control** — drives all outputs through opto-isolators or dedicated driver boards (see `docs/gpio-safety.md`):
  - Dispenser motor enable.
  - Drawer latch/lock solenoid.
  - Bill acceptor enable.
  - Status LEDs and beeper.
- **Transaction state machine** — implements the state machine defined in `docs/architecture.md`.  
  No actuator command may be issued outside a valid state transition.
- **IPC server** — exposes a Unix domain socket interface for the Kiosk UI (command/event protocol; see `docs/architecture.md`).
- **Watchdog management** — pets the Raspberry Pi hardware watchdog (`/dev/watchdog`) on a regular interval.  
  On any unhandled fault, stops petting to trigger a system reboot.
- **Logging** — records all state transitions, sensor events, and faults with timestamps for audit and reconciliation.

## Planned Technology

- **Node.js** or **Python** (TBD — to be decided based on GPIO library availability and team preference).
- Runs as a `systemd` service with appropriate restart and after-network-up settings.
- Starts before the Kiosk UI and exposes the IPC socket.

## Safe Default States

On startup and on any fault/reboot, all outputs must be in the safe default state before accepting any command from the Kiosk UI:

| Output | Safe Default |
|---|---|
| Dispenser enable | **OFF** |
| Drawer latch | **Locked** |
| Bill acceptor enable | **OFF** |

See `docs/gpio-safety.md` for the full safe-state table and hardware pull-resistor requirements.

## Getting Started (placeholder)

This directory is not yet implemented.  
See `docs/architecture.md` for the IPC interface this module must expose.  
See `docs/safety.md` and `docs/gpio-safety.md` for all safety requirements this module must satisfy.
