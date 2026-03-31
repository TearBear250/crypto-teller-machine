"""Sell (cash-out) flow screen.

Steps:
  1. Enter dollar amount to receive.
  2. Fetch quote from backend.
  3. Create transaction.
  4. Show simulated deposit instructions.
  5. Simulate deposit confirmed (button).
  6. Simulate cash dispensed.
"""
from __future__ import annotations

import json
import tkinter as tk
import uuid
from datetime import datetime, timezone
from typing import Optional

from kiosk.screens.base import (
    BaseScreen, BG, FG, ACCENT, ACCENT2, SUCCESS, FONT_BODY, FONT_SMALL,
    styled_button,
)
from kiosk.db import connect, upsert_local_tx, enqueue_event
from shared.models import QuoteRequest, TxCreateRequest

# Simulated deposit address shown to user
_SIMULATED_DEPOSIT_ADDRESS = "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"


class SellScreen(BaseScreen):
    def build(self) -> None:
        self._title("Sell BTC → Cash")

        self._label("Enter CAD amount to receive:")
        self._amount_var = tk.StringVar(value="100")
        tk.Entry(
            self,
            textvariable=self._amount_var,
            font=("Arial", 32),
            width=10,
            justify="center",
            bg="#0f3460",
            fg=FG,
            insertbackground=FG,
        ).pack(pady=10)

        styled_button(self, text="Get Quote", command=self._get_quote, bg=ACCENT2).pack(
            pady=15, ipadx=10, ipady=8
        )

        self._quote_label = tk.Label(self, text="", font=FONT_BODY, bg=BG, fg=SUCCESS)
        self._quote_label.pack(pady=8)

        self._proceed_btn = styled_button(
            self, text="Create Transaction", command=self._create_tx, bg="#333366"
        )
        self._proceed_btn.pack(pady=10, ipadx=10, ipady=8)
        self._proceed_btn.config(state=tk.DISABLED)

        self._deposit_frame = tk.Frame(self, bg=BG)
        self._deposit_frame.pack(pady=8)
        self._deposit_label = tk.Label(
            self._deposit_frame, text="", font=FONT_SMALL, bg=BG, fg="#aaddff"
        )
        self._deposit_label.pack()

        self._confirm_btn = styled_button(
            self,
            text="✅ Simulate Deposit Confirmed",
            command=self._simulate_deposit_confirmed,
            bg="#004400",
        )
        self._confirm_btn.pack(pady=10, ipadx=10, ipady=8)
        self._confirm_btn.config(state=tk.DISABLED)

        self._dispense_btn = styled_button(
            self,
            text="💵 Simulate Cash Dispensed",
            command=self._simulate_cash_dispensed,
            bg="#440044",
        )
        self._dispense_btn.pack(pady=10, ipadx=10, ipady=8)
        self._dispense_btn.config(state=tk.DISABLED)

        self._status_label = tk.Label(self, text="", font=FONT_BODY, bg=BG, fg=SUCCESS)
        self._status_label.pack(pady=8)

        self._back_button()

        self._quote: Optional[dict] = None
        self._tx: Optional[dict] = None

    def on_show(self) -> None:
        self._quote = None
        self._tx = None
        self._quote_label.config(text="")
        self._deposit_label.config(text="")
        self._status_label.config(text="")
        self._proceed_btn.config(state=tk.DISABLED)
        self._confirm_btn.config(state=tk.DISABLED)
        self._dispense_btn.config(state=tk.DISABLED)

    # ------------------------------------------------------------------

    def _get_quote(self) -> None:
        try:
            dollars = float(self._amount_var.get().strip())
            if dollars <= 0:
                raise ValueError("Amount must be positive")
            cents = int(round(dollars * 100))
            req = QuoteRequest(side="sell", asset="BTC", fiat="CAD", fiat_amount=cents)
            self._quote = self.app.api.create_quote(req)
            asset = self._quote["asset_amount"]
            fee_cad = self._quote["fee_fiat_amount"] / 100
            self._quote_label.config(
                text=f"Send ≈ {asset} BTC  (fee: ${fee_cad:.2f} CAD)"
            )
            self._proceed_btn.config(state=tk.NORMAL)
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
                side="sell",
                asset="BTC",
                fiat="CAD",
                fiat_amount=cents,
                idempotency_key=idem,
                payout_address=None,
            )
            self._tx = self.app.api.create_tx(req)
            tx_id = self._tx["tx_id"]

            conn = connect()
            upsert_local_tx(
                conn,
                tx_id=tx_id,
                status=self._tx["status"],
                side="sell",
                fiat_amount=cents,
                asset_amount=self._quote["asset_amount"],
                created_at_utc=datetime.now(timezone.utc).isoformat(),
            )
            conn.close()

            self._proceed_btn.config(state=tk.DISABLED)
            self._deposit_label.config(
                text=f"Send {self._quote['asset_amount']} BTC to:\n{_SIMULATED_DEPOSIT_ADDRESS}"
                     f"\n(simulated – no real funds)"
            )
            self._confirm_btn.config(state=tk.NORMAL)
            self._status_label.config(
                text=f"TX: {tx_id[:8]}…  Status: awaiting_deposit", fg=SUCCESS
            )
        except Exception as exc:
            self._status_label.config(text=f"Error: {exc}", fg="#ff4444")

    def _simulate_deposit_confirmed(self) -> None:
        if not self._tx:
            return
        try:
            tx_id = self._tx["tx_id"]
            cents = int(round(float(self._amount_var.get().strip()) * 100))
            conn = connect()
            enqueue_event(conn, tx_id, "deposit_confirmed", "{}")
            upsert_local_tx(conn, tx_id, "dispensing", "sell", cents)
            conn.close()

            self._confirm_btn.config(state=tk.DISABLED)
            self._dispense_btn.config(state=tk.NORMAL)
            self._status_label.config(
                text=f"Deposit confirmed!\nTX: {tx_id[:8]}…  Status: dispensing", fg=SUCCESS
            )
        except Exception as exc:
            self._status_label.config(text=f"Error: {exc}", fg="#ff4444")

    def _simulate_cash_dispensed(self) -> None:
        if not self._tx:
            return
        try:
            tx_id = self._tx["tx_id"]
            dollars = float(self._amount_var.get().strip())
            cents = int(round(dollars * 100))

            ok = self.app.cash_dispenser.dispense(cents)
            if not ok:
                raise RuntimeError("Dispenser out of cash – please see operator")

            conn = connect()
            enqueue_event(
                conn, tx_id, "cash_dispensed",
                json.dumps({"amount_cents": cents})
            )
            upsert_local_tx(conn, tx_id, "completed", "sell", cents)
            conn.close()

            self._dispense_btn.config(state=tk.DISABLED)
            self._status_label.config(
                text=f"💵 ${dollars:.2f} CAD dispensed!\nTransaction complete.",
                fg=SUCCESS,
            )

            # Print simulated receipt
            self.app.receipt_printer.print_receipt([
                f"  Crypto Teller Machine  ",
                f"  SELL BTC               ",
                f"  Amount: ${dollars:.2f} CAD   ",
                f"  TX: {tx_id[:16]}…",
                f"  Thank you!             ",
            ])
        except Exception as exc:
            self._status_label.config(text=f"Error: {exc}", fg="#ff4444")
