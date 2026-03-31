"""Buy (cash-in) flow screen.

Steps:
  1. Enter dollar amount.
  2. Fetch quote from backend.
  3. Create transaction.
  4. Simulate cash insertion (button).
  5. Show transaction status / confirmation.
"""
from __future__ import annotations

import json
import tkinter as tk
import uuid
from datetime import datetime, timezone
from typing import Optional

from kiosk.screens.base import (
    BaseScreen, BG, FG, ACCENT, SUCCESS, FONT_BODY, FONT_SMALL,
    styled_button,
)
from kiosk.db import connect, upsert_local_tx, enqueue_event
from shared.models import QuoteRequest, TxCreateRequest


class BuyScreen(BaseScreen):
    def build(self) -> None:
        self._title("Buy BTC")

        self._label("Enter amount (CAD $):")
        self._amount_var = tk.StringVar(value="100")
        amount_entry = tk.Entry(
            self,
            textvariable=self._amount_var,
            font=("Arial", 32),
            width=10,
            justify="center",
            bg="#0f3460",
            fg=FG,
            insertbackground=FG,
        )
        amount_entry.pack(pady=10)

        styled_button(self, text="Get Quote", command=self._get_quote).pack(
            pady=15, ipadx=10, ipady=8
        )

        self._quote_label = tk.Label(self, text="", font=FONT_BODY, bg=BG, fg=SUCCESS)
        self._quote_label.pack(pady=8)

        self._proceed_btn = styled_button(
            self,
            text="Create Transaction",
            command=self._create_tx,
            bg="#333366",
        )
        self._proceed_btn.pack(pady=10, ipadx=10, ipady=8)
        self._proceed_btn.config(state=tk.DISABLED)

        self._insert_btn = styled_button(
            self,
            text="💵 Simulate Cash Inserted",
            command=self._simulate_cash_inserted,
            bg="#444400",
        )
        self._insert_btn.pack(pady=10, ipadx=10, ipady=8)
        self._insert_btn.config(state=tk.DISABLED)

        self._status_label = tk.Label(self, text="", font=FONT_BODY, bg=BG, fg=SUCCESS)
        self._status_label.pack(pady=8)

        self._back_button()

        # State
        self._quote: Optional[dict] = None
        self._tx: Optional[dict] = None

    def on_show(self) -> None:
        self._quote = None
        self._tx = None
        self._quote_label.config(text="")
        self._status_label.config(text="")
        self._proceed_btn.config(state=tk.DISABLED)
        self._insert_btn.config(state=tk.DISABLED)

    # ------------------------------------------------------------------

    def _get_quote(self) -> None:
        try:
            dollars = float(self._amount_var.get().strip())
            if dollars <= 0:
                raise ValueError("Amount must be positive")
            cents = int(round(dollars * 100))
            req = QuoteRequest(side="buy", asset="BTC", fiat="CAD", fiat_amount=cents)
            self._quote = self.app.api.create_quote(req)
            asset = self._quote["asset_amount"]
            fee_cad = self._quote["fee_fiat_amount"] / 100
            self._quote_label.config(
                text=f"≈ {asset} BTC  (fee: ${fee_cad:.2f} CAD)\nQuote valid 2 min"
            )
            self._proceed_btn.config(state=tk.NORMAL)
            self._status_label.config(text="")
        except Exception as exc:
            self._quote_label.config(text=f"Error: {exc}", fg="#ff4444")

    def _create_tx(self) -> None:
        if not self._quote:
            return
        try:
            dollars = float(self._amount_var.get().strip())
            cents = int(round(dollars * 100))
            idem = str(uuid.uuid4())
            req = TxCreateRequest(
                side="buy",
                asset="BTC",
                fiat="CAD",
                fiat_amount=cents,
                idempotency_key=idem,
                payout_address=None,
            )
            self._tx = self.app.api.create_tx(req)
            tx_id = self._tx["tx_id"]

            # Persist to local SQLite
            conn = connect()
            upsert_local_tx(
                conn,
                tx_id=tx_id,
                status=self._tx["status"],
                side="buy",
                fiat_amount=cents,
                asset_amount=self._quote["asset_amount"],
                created_at_utc=datetime.now(timezone.utc).isoformat(),
            )
            conn.close()

            self._status_label.config(
                text=f"TX created: {tx_id[:8]}…\nStatus: {self._tx['status']}", fg=SUCCESS
            )
            self._proceed_btn.config(state=tk.DISABLED)
            self._insert_btn.config(state=tk.NORMAL)

            # Activate cash acceptor
            self.app.cash_acceptor.reset()
            self.app.cash_acceptor.start_accepting()
        except Exception as exc:
            self._status_label.config(text=f"Error: {exc}", fg="#ff4444")

    def _simulate_cash_inserted(self) -> None:
        if not self._tx:
            return
        try:
            tx_id = self._tx["tx_id"]
            dollars = float(self._amount_var.get().strip())
            cents = int(round(dollars * 100))

            # Simulate the hardware event
            self.app.cash_acceptor.simulate_insert(cents)
            self.app.cash_acceptor.stop_accepting()

            # Queue event for backend sync
            conn = connect()
            enqueue_event(
                conn,
                tx_id=tx_id,
                event_type="cash_inserted",
                payload_json=json.dumps({"amount_cents": cents}),
            )
            upsert_local_tx(conn, tx_id, "executing", "buy", cents)
            conn.close()

            self._insert_btn.config(state=tk.DISABLED)
            self._status_label.config(
                text=f"💵 Cash inserted: ${dollars:.2f} CAD\n"
                     f"TX: {tx_id[:8]}…  Status: executing\n"
                     f"Crypto will be sent to your wallet.",
                fg=SUCCESS,
            )
        except Exception as exc:
            self._status_label.config(text=f"Error: {exc}", fg="#ff4444")
