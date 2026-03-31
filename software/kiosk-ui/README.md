# Kiosk UI

Placeholder for the CTM Kiosk UI application.

## Responsibility

The Kiosk UI is a fullscreen, touch-friendly application running on the Raspberry Pi's display.  
It presents the user transaction flow and communicates with the Device Daemon (via local IPC) and Backend Services (via HTTPS).

## Planned Technology

- **Electron** shell for fullscreen kiosk mode on Linux/ARM.
- **React** for the UI component tree.
- **Vite** as the build tool.

No user should ever be able to exit the kiosk application to the desktop OS during normal operation.

## Key Screens (planned)

1. **Idle / Welcome** — attract loop, coin selection prompt.
2. **Transaction Type** — Buy (cash in) or Sell (cash out).
3. **Coin Selection** — BTC, LTC, DOGE, XRP, SOL, others.
4. **Amount Entry** — fiat amount or crypto amount with live rate.
5. **QR / Address** — user wallet address input for cash-out; display address for cash-in.
6. **Processing** — in-progress spinner while backend confirms payment.
7. **Dispense** — animated countdown for drawer unlock; "Remove your cash now" prompt.
8. **Confirmation** — receipt option; souvenir token notice (if token dispenser enabled).
9. **Fault / Out of Service** — user-facing error screen with support contact.

## Getting Started (placeholder)

This directory is not yet implemented.  
See `docs/architecture.md` for the IPC interface this module must implement.

## Safety Notes

- This module must never access GPIO or hardware directly.
- All hardware commands must go through the Device Daemon IPC interface.
- The UI must not instruct users to insert body parts into any machine opening.
- Souvenir tokens must be described as "collectible tokens — no cash value" in all UI copy.
