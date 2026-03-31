# Crypto Teller Machine – MVP

A safe, touch-first crypto teller machine prototype built with **Python**, **FastAPI**, **Tkinter**, and **SQLite**.

> **Disclaimer:** This is a development scaffold with simulated cash hardware.  
> No real cash, crypto, or financial services are exchanged.

---

## Repository layout

```
crypto-teller-machine/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── db.py            # SQLite helpers (backend)
│   │   └── routers/
│   │       └── transactions.py  # /v1/quotes, /v1/transactions, /v1/health
│   └── tests/
│       ├── conftest.py
│       ├── test_health.py
│       └── test_transactions.py
├── kiosk/
│   ├── app.py               # Entry point – run this
│   ├── api_client.py        # HTTP wrapper for backend
│   ├── db.py                # SQLite helpers (kiosk local state + event queue)
│   ├── sync_worker.py       # Background thread: flush events to backend
│   ├── devices/
│   │   └── hardware.py      # Device abstraction + simulator implementations
│   └── screens/
│       ├── base.py          # Shared UI helpers
│       ├── home.py          # Home / attract screen
│       ├── buy.py           # Buy (cash-in) flow
│       └── sell.py          # Sell (cash-out) flow
├── shared/
│   └── models.py            # Pydantic models shared by backend and kiosk
├── requirements.txt
├── pytest.ini
└── README.md
```

---

## Prerequisites

- Python 3.11+
- `tkinter` (usually bundled with CPython; on Debian/Ubuntu: `sudo apt install python3-tk`)

---

## Quick start

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start the backend

```bash
uvicorn backend.app.main:app --reload
```

The API is now available at <http://127.0.0.1:8000>.  
Interactive docs: <http://127.0.0.1:8000/docs>

### 3. Start the kiosk (new terminal, same venv)

```bash
# Full-screen kiosk mode (default):
python kiosk/app.py

# Windowed mode for desktop development:
CTM_WINDOWED=1 python kiosk/app.py
```

Press **Escape** to exit full-screen mode.

### 4. Run the tests

```bash
pytest
```

---

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/v1/health` | Health check |
| `POST` | `/v1/quotes` | Placeholder price quote |
| `POST` | `/v1/transactions` | Create transaction (idempotency key required) |
| `GET`  | `/v1/transactions/{tx_id}` | Get transaction status |
| `POST` | `/v1/transactions/{tx_id}/events` | Record kiosk event (cash_inserted, cash_dispensed, …) |

---

## Kiosk flows

### Buy (cash-in)

1. Enter dollar amount → tap **Get Quote**  
2. Review quote → tap **Create Transaction**  
3. Tap **Simulate Cash Inserted** (replaces real bill acceptor)  
4. Status updates to `executing`; background worker syncs event to backend  

### Sell (cash-out)

1. Enter dollar amount → tap **Get Quote**  
2. Review quote → tap **Create Transaction**  
3. Deposit instructions shown (simulated address)  
4. Tap **Simulate Deposit Confirmed** → status advances to `dispensing`  
5. Tap **Simulate Cash Dispensed** → receipt printed to console, status → `completed`  

---

## Device abstraction

`kiosk/devices/hardware.py` defines abstract base classes:

- `CashAcceptor` – enable/disable bill slot, read inserted amount  
- `CashDispenser` – dispense notes, check cassette level  
- `ReceiptPrinter` – print receipt lines  

Simulator classes (`SimulatedCash*`, `SimulatedReceiptPrinter`) are wired in
`kiosk/app.py`.  To integrate real hardware, implement the abstract classes
using your vendor's official SDK and swap them in `KioskApp.__init__`.

---

## Safety notes

- Cash hardware is **fully simulated**; no ATM vendor protocols or reverse-engineering toolkits are included.  
- Sensitive data (PINs, keys, wallet addresses) should never be stored in SQLite; use a secrets manager.  
- Replace placeholder pricing in `backend/app/routers/transactions.py` with a real exchange integration before production use.

The original mission for this machine: safety protocols to prevent fraud against blockchain altcoins and crypto, plus counterfeit-bill detection for transactions.

