# Crypto Teller Machine

A desktop touchscreen kiosk application for generating paper wallets / vouchers for cryptocurrency denominations.

## Milestone 1 — Supported Coins

| Coin | Symbol | Status |
|------|--------|--------|
| Bitcoin Cash | BCH | ✅ Supported |
| Litecoin | LTC | ✅ Supported |
| Dogecoin | DOGE | ✅ Supported |
| XRP | XRP | 🔜 Coming Soon |
| Solana | SOL | 🔜 Coming Soon |

## Setup & Running

### Prerequisites
- [Node.js](https://nodejs.org/) v18 or later
- npm v9 or later

### Install dependencies
```bash
npm install
```

### Run in development mode (Electron + Vite hot-reload)
```bash
npm run dev
```

This starts the Vite dev server and launches the Electron window automatically.

### Build for production (web bundle only)
```bash
npm run build
```

Output goes to `dist/`.

### Run Electron against built output
```bash
npm run electron
```

### Preview built web UI in browser
```bash
npm run preview
```

## User Flow

1. **Home screen** — Select a cryptocurrency (BCH, LTC, or DOGE).
2. **Denomination screen** — Choose a coin amount ($0.01–$2.00) or bill denomination ($1–$1,000).
3. **Voucher screen** — A paper wallet is generated with:
   - Currency name and symbol
   - Receiving address (text)
   - QR code for the receiving address
   - **Print** button (uses Electron print or browser `window.print()`)

## Denominations

Denominations are configurable in [`denominations.json`](./denominations.json):

```json
{
  "coins": [0.01, 0.05, 0.10, 0.25, 0.50, 1.00, 2.00],
  "bills": [1, 5, 10, 20, 50, 100, 1000]
}
```

> **TODO:** Confirm final denomination sets with stakeholders, including exact coin denominations ($0.01–$2.00) and high-value bills/collector vouchers.

## Architecture

```
crypto-teller-machine/
├── electron/
│   ├── main.js          # Electron main process (BrowserWindow + IPC)
│   └── preload.js       # Secure context bridge (window.electronAPI)
├── src/
│   ├── components/
│   │   ├── HomeScreen.jsx        # Coin selection
│   │   ├── DenominationScreen.jsx # Denomination selection
│   │   └── VoucherScreen.jsx     # QR code + print
│   ├── services/
│   │   └── walletService.js      # Address generation (BCH/LTC/DOGE)
│   ├── utils/
│   │   └── formatAmount.js       # Currency formatting
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── denominations.json   # Configurable denomination list
├── index.html
├── vite.config.js
└── package.json
```

## Security & Privacy

- **Private keys are never stored** on disk or in application state.
- Address generation uses `bitcoinjs-lib` + `tiny-secp256k1` (industry-standard libraries).
- The Electron preload uses `contextIsolation: true` and `nodeIntegration: false`.

## Current Limitations

- XRP and Solana address generation are not yet implemented (stubs only).
- No exchange rate / fiat-value lookup in this milestone.
- No bill acceptor / payment hardware integration yet.
- Denominations represent voucher face values, not live exchange amounts.
- Denomination color-coding (Canadian currency-inspired) is a future design milestone. 
