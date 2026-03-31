# CTM Physical Safety Requirements

This document defines mandatory physical safety requirements for the Crypto Teller Machine (CTM) enclosure.  
Every design revision must be checked against this list before fabrication or assembly.

---

## 1. Entanglement Prevention

Moving mechanisms inside the CTM (bill transport, dispenser rollers, receipt cutter) present entanglement hazards if accessible.

**Requirements:**

- All rollers, belts, gears, and moving linkages **must** be fully enclosed behind rigid internal barriers with no user-accessible gaps.
- Every user-facing opening (bill slot, receipt slot, drawer pocket) **must** be sized to allow the intended item (bill, receipt, banknote) while preventing finger or hair insertion.
  - Maximum slot width: **1 mm wider than the thickest acceptable bill**.
  - Slot depth before internal mechanism: **≥ 50 mm of empty chute** (no moving parts reachable).
- Brush gaskets or foam seals **must** be fitted around all slot openings to:
  - Prevent hair, clothing fabric, or flexible material from being drawn inward.
  - Close the gap when no item is present.
- No rotating mechanism may be reachable from any external surface without tools.

---

## 2. Pinch Points and Sharp Edges

**Requirements:**

- All user-accessible surfaces and edges **must** be radiused (minimum R 1.5 mm) or chamfered.
- No exposed sheet-metal cut edges on exterior panels — use plastic trim or deburred rolled edges.
- The drawer opening (user pocket rim) **must** use a rounded plastic trim strip on all four edges.
- The cash drawer travel path **must** include side clearances that prevent fingers from being caught between drawer and frame. Minimum side clearance: **8 mm** or a fixed guard that prevents lateral finger insertion.
- Any door or panel that swings or slides on the enclosure **must** use soft-close dampers or restricted travel stops to limit closing force.

---

## 3. Drawer Geometry and Two-Chamber Separation

The cash-out payout pocket uses a drawer-style design to physically separate the user from the dispenser mechanism.

```
  ┌─────────────────────────────────────┐
  │          MACHINE SIDE               │
  │  [Bill Dispenser]                   │
  │       │                             │
  │       ▼                             │
  │  [Drop Chute / Baffle]  ←── Baffle prevents reach-through
  │       │                             │
  ├───────┼─────────────────────────────┤  ← Internal divider wall
  │       ▼                             │
  │  [Cash Pocket]  ← drawer slides out │
  │                                     │
  │          USER SIDE                  │
  └─────────────────────────────────────┘
```

**Requirements:**

- The enclosure **must** implement a **two-chamber design**: an inner machine chamber (dispenser + chute) and an outer user chamber (drawer pocket).
- The chambers **must** be separated by a rigid divider wall with a drop opening sized for bills only (≤ 10 mm clearance around bill width).
- The drop opening **must** include a **gravity flap or shutter** that:
  - Opens only when a bill is actively being dispensed.
  - Returns to the closed position under gravity or a light spring when no bill is present.
- The chute geometry from the drop opening to the cash pocket **must** be offset (non-straight) so that no direct line of sight or reach exists from the user pocket to the dispenser mechanism.
- The drawer travel distance **must** be limited so that the drawer cannot be pulled far enough to expose the drop chute opening.

---

## 4. Interlocks

### 4.1 Drawer-Closed Interlock

- The dispenser **must not** run unless a **hardware interlock confirms the drawer is closed**.
- The drawer-closed signal **must** be in the hardware enable path of the dispenser motor driver — not solely a software check.
- Sensor: a microswitch or magnetic reed switch mounted so that drawer closure reliably engages it.

### 4.2 Stop on Open

- If the drawer opens or the drawer-closed sensor de-asserts **at any time** (including during a dispense cycle):
  - **Immediately stop all actuator motion** (hardware path preferred; software as secondary enforcement).
  - Flag the transaction as `INTERRUPTED`.
  - Lock the drawer latch (if electromechanical) until a recovery action is initiated.

### 4.3 Cabinet Tamper Switch

- A tamper switch **must** be fitted to the main service door.
- Opening the service door during operation **must**:
  - Stop all actuators.
  - Log the event with timestamp.
  - Require authenticated service-mode reset before normal operation resumes.

### 4.4 Safe Default States

| Signal | Safe (Default) State |
|---|---|
| Dispenser motor enable | **OFF** |
| Drawer latch/lock | **Locked** |
| Bill acceptor enable | **OFF** |
| Receipt cutter | **Retracted / safe** |

All outputs **must** default to their safe state on power-up and on any watchdog reset.

---

## 5. Software Fault Handling

### 5.1 Transaction State Machine

All transaction logic **must** be implemented as an explicit state machine (defined in `docs/architecture.md`).  
No action may be taken outside a defined state transition.

### 5.2 Stop Rules

The device daemon **must** immediately transition to `FAULT` state and halt actuators when any of the following occur:

- Drawer sensor contradicts expected state.
- Motor current exceeds threshold (jam detection).
- Bill count or dispenser sensor mismatch detected.
- Watchdog timeout (Pi unresponsive).
- Any unhandled exception in the daemon process.

### 5.3 Recovery Rules

- The system **must** log the fault state, sensor readings, and last transaction ID before halting.
- Recovery from `FAULT` requires an explicit authenticated reset action (not an automatic retry).
- Automatic retries of actuator commands are **prohibited** when a jam or unexpected sensor state is present.

---

## 6. Signage and UI Warnings

**Physical signage requirements:**

- A permanent label **must** be placed at each user-facing opening:
  - Bill acceptor slot: **"Insert bills only — do not insert fingers or objects"**
  - Drawer pocket: **"Remove cash from pocket — do not reach into machine"**
  - Receipt slot: **"Remove receipt only"**
- Labels must be durable (engraved, UV-printed, or equivalent — not paper stickers).
- Minimum label character height: **5 mm** for legibility.

**On-screen UI requirements:**

- Display an animated or timed prompt **"Remove your cash now"** with a visible countdown when the drawer latch releases.
- After countdown expires, re-lock the drawer and show a "Transaction complete" screen.
- At no point should the UI instruct a user to insert their hand, arm, or any body part into any opening.

---

## 7. Design Review Checklist

Before finalizing any enclosure revision, verify all of the following:

- [ ] All rotating and moving parts are fully enclosed with no user-accessible gaps.
- [ ] All slot openings are brush-gasketed and sized to bill/receipt width only.
- [ ] All external edges are radiused ≥ R 1.5 mm or chamfered.
- [ ] Two-chamber drawer design with offset baffle chute is implemented.
- [ ] Gravity flap or shutter is fitted at the drop opening.
- [ ] Drawer-closed hardware interlock is wired into motor driver enable path.
- [ ] Stop-on-open behavior verified in bench test.
- [ ] Tamper switch fitted on service door.
- [ ] All safe default states verified at power-up.
- [ ] Signage labels installed at each opening.
- [ ] State machine fault/stop/recovery logic reviewed.
