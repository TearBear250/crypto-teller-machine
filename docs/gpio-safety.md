# CTM Raspberry Pi GPIO Safety Guidelines

This document defines safe practices for using Raspberry Pi GPIO in the CTM.  
Violating these guidelines risks hardware damage, fire, or unsafe actuator behavior.

---

## 1. Never Drive Actuators Directly from GPIO

Raspberry Pi GPIO pins are **3.3 V logic, low-current outputs** (≤ 16 mA per pin, 50 mA total).  
They are **not** capable of driving solenoids, motors, relays, locks, or other actuators directly.

**Requirements:**

- Every GPIO output connected to an actuator or load **must** go through an appropriate driver stage:
  - **Opto-isolator** (preferred for safety-critical lines) — provides galvanic isolation between Pi logic and power circuits.
  - **MOSFET driver board** (e.g., ULN2003/ULN2803 for small solenoids; dedicated motor driver IC for larger loads).
  - **Solid-state relay (SSR)** for higher-current AC or DC loads.
- Never connect a GPIO pin directly to a relay coil, solenoid coil, motor terminal, or any inductive load.
- Coil-based actuators (solenoids, relay coils, motor windings) **must** have **flyback diodes** (1N4007 or equivalent) fitted across the coil terminals to suppress back-EMF.

---

## 2. Separate Power Rails

**Requirements:**

- Actuators (dispenser motor, drawer lock solenoid, bill acceptor) **must** run on a **dedicated power supply** that is separate from the Raspberry Pi's 5 V supply.
- The Pi's 5 V rail powers only: the Pi itself and low-power logic/sensor boards.
- Power rail separation prevents actuator current spikes from resetting or damaging the Pi.
- Use a common ground between rails **only** at a single star point to avoid ground loops.
- Label power rails clearly in wiring diagrams (e.g., `+5V_PI`, `+12V_ACT`, `+24V_LOCK`).

---

## 3. ESD Protection and Long Cable Runs

GPIO pins are ESD-sensitive. Cables leaving the main PCB/enclosure area are particularly vulnerable.

**Requirements:**

- Add a **series resistor (330 Ω–1 kΩ)** on every GPIO output line that leaves the immediate board area.
- Add **TVS (transient voltage suppression) diodes** or a protection IC (e.g., SP0504BAHTG) on signal lines that run to remote sensors or switches (drawer sensors, tamper switch).
- Use **shielded cable** for sensor runs longer than 150 mm; connect shield to chassis ground at one end only.
- Fit **strain relief** on all cables at the enclosure penetration point.
- If any external sensor or board outputs **5 V logic**, use a **level-shifter** before connecting to the Pi GPIO — do not connect 5 V directly to a 3.3 V Pi GPIO input.

---

## 4. Pull-ups, Pull-downs, and Debounce

**Requirements:**

- All switch inputs (drawer closed, drawer open, tamper switch) **must** have a defined rest state via pull-up or pull-down:
  - Normally-closed (NC) switches: configure GPIO with internal pull-up; switch pulls to GND when open.
  - Normally-open (NO) switches: configure GPIO with internal pull-down; switch pulls to 3.3 V when closed.
- Preferred: **NC switches for safety-critical interlocks** so that a broken wire or disconnected sensor fails to the "unsafe / open" state, triggering a fault rather than allowing spurious operation.
- Implement **software debounce** (minimum 20 ms filter) on all mechanical switch inputs.
- For higher-noise environments, add a hardware RC debounce (100 Ω + 100 nF) on the input line.

---

## 5. Safe Default States and Boot Behavior

**Requirements:**

- All GPIO outputs **must** default to their safe state at power-on and remain there until explicitly commanded by verified application code.
- Do not rely on Linux userspace startup to enforce safe defaults — use hardware pull-down resistors on driver enable lines so that the driver is disabled even before the Pi boots.
- Safe default state table for the drawer subsystem:

  | Signal | Direction | Safe Default | Pull Resistor |
  |---|---|---|---|
  | `DISPENSER_ENABLE` | Output | **LOW (disabled)** | Pull-down on driver input |
  | `DRAWER_LOCK` | Output | **HIGH (locked)** | Pull-up to lock coil driver |
  | `BILL_ACCEPTOR_ENABLE` | Output | **LOW (disabled)** | Pull-down on driver input |
  | `DRAWER_CLOSED_SENSE` | Input | — | Pull-up (NC switch) |
  | `DRAWER_OPEN_SENSE` | Input | — | Pull-up (NC switch) |
  | `TAMPER_SENSE` | Input | — | Pull-up (NC switch) |
  | `CASH_PRESENT_SENSE` | Input | — | Pull-down (NO sensor) |

---

## 6. Watchdog Considerations

A software fault or kernel hang on the Pi should not leave actuators in an active state.

**Requirements:**

- Enable the **Raspberry Pi hardware watchdog** (`/dev/watchdog`) in the device daemon. The daemon must "pet" the watchdog on a regular interval; if it fails to do so, the Pi reboots.
- After watchdog reboot, all GPIO outputs return to safe defaults via hardware pull resistors (see Section 5).
- Consider an **external watchdog supervisor IC** (e.g., MAX6369) to cut driver enable lines if the Pi's watchdog heartbeat output stops toggling, independent of software.
- The device daemon must register a clean shutdown handler that drives all outputs to safe state before exiting.

---

## 7. Recommended GPIO Signal List — Drawer Subsystem

The following signals are recommended for the drawer and payout subsystem.  
Exact GPIO pin numbers are assigned in the device daemon configuration.

### Inputs (Pi receives)

| Signal Name | Type | Description |
|---|---|---|
| `DRAWER_CLOSED_SENSE` | Digital in | NC microswitch: LOW when drawer is open |
| `DRAWER_OPEN_SENSE` | Digital in | NC microswitch: LOW when drawer is fully closed (optional, provides positive confirmation of full extension) |
| `CASH_PRESENT_SENSE` | Digital in | Optical or IR sensor: HIGH when cash is in the pocket |
| `TAMPER_SENSE` | Digital in | NC microswitch on service door: LOW when door is open |
| `DISPENSER_FAULT` | Digital in | Fault signal from dispenser driver board |
| `BILL_ACCEPTOR_STATUS` | Serial/USB | ccTalk or MDB protocol (not a simple GPIO) |

### Outputs (Pi drives — through opto/driver only)

| Signal Name | Type | Description |
|---|---|---|
| `DISPENSER_ENABLE` | Digital out → driver | Enable dispenser motor driver; LOW = disabled |
| `DRAWER_LOCK` | Digital out → driver | Control drawer latch solenoid; requires flyback diode |
| `BILL_ACCEPTOR_ENABLE` | Digital out → driver | Enable/disable bill acceptor transport |
| `STATUS_LED_R/G/B` | Digital out | Indicator LEDs (optional; current-limited via resistor) |
| `BEEPER` | Digital out | Audible alert (through transistor driver) |

---

## 8. Quick Reference — Do and Don't

| ✅ Do | ❌ Don't |
|---|---|
| Use opto-isolators or driver boards for all actuators | Connect a solenoid or motor directly to GPIO |
| Put flyback diodes on all coil loads | Omit flyback protection on relay/solenoid coils |
| Use separate power rails for Pi and actuators | Power actuators from the Pi's 5 V pin |
| Hardware pull-down on driver enables | Rely solely on software for safe-off behavior |
| Use NC switches for safety interlocks | Use NO switches for critical safety signals |
| Add series resistors on output lines off-board | Run bare GPIO wires to remote components |
| Level-shift any 5 V sensor signal before Pi GPIO | Connect 5 V logic directly to Pi GPIO input |
| Pet the hardware watchdog from the daemon | Leave watchdog unconfigured in production |
