"""Crypto Teller Machine – Kiosk application entry point.

Run with::

    python kiosk/app.py

The window opens full-screen by default (touch-first kiosk mode).
Set the ``CTM_WINDOWED`` environment variable to ``1`` for a 900×700 window
during development on a desktop:

    CTM_WINDOWED=1 python kiosk/app.py
"""
from __future__ import annotations

import logging
import os
import sys
import tkinter as tk
from pathlib import Path

# ---------------------------------------------------------------------------
# Ensure project root is on sys.path so ``shared`` and ``kiosk`` are importable
# when this file is executed directly with ``python kiosk/app.py``.
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from kiosk.api_client import ApiClient
from kiosk.db import init_db
from kiosk.devices.hardware import (
    SimulatedCashAcceptor,
    SimulatedCashDispenser,
    SimulatedReceiptPrinter,
)
from kiosk.sync_worker import SyncWorker
from kiosk.screens.base import BG
from kiosk.screens.home import HomeScreen
from kiosk.screens.buy import BuyScreen
from kiosk.screens.sell import SellScreen

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

BACKEND_BASE_URL = os.environ.get("CTM_BACKEND_URL", "http://127.0.0.1:8000")
WINDOWED = os.environ.get("CTM_WINDOWED", "0") == "1"


class KioskApp(tk.Tk):
    """Root Tkinter application.  Manages screen transitions and shared state."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Crypto Teller Machine")

        if WINDOWED:
            self.geometry("900x700")
        else:
            self.attributes("-fullscreen", True)
            self.bind("<Escape>", lambda _e: self.attributes("-fullscreen", False))

        self.configure(bg=BG)
        self.resizable(True, True)

        # ------------------------------------------------------------------
        # Shared services (injectable – swap real devices here)
        # ------------------------------------------------------------------
        self.api = ApiClient(BACKEND_BASE_URL)
        self.cash_acceptor = SimulatedCashAcceptor()
        self.cash_dispenser = SimulatedCashDispenser()
        self.receipt_printer = SimulatedReceiptPrinter()

        # ------------------------------------------------------------------
        # Local database
        # ------------------------------------------------------------------
        init_db()

        # ------------------------------------------------------------------
        # Background sync worker
        # ------------------------------------------------------------------
        self._sync = SyncWorker(self.api, poll_interval=5.0)
        self._sync.start()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # ------------------------------------------------------------------
        # Screens
        # ------------------------------------------------------------------
        self._screens: dict[str, tk.Frame] = {}
        self._build_screens()
        self.show_home()

    # ------------------------------------------------------------------
    # Screen management
    # ------------------------------------------------------------------

    def _build_screens(self) -> None:
        for name, cls in [
            ("home", HomeScreen),
            ("buy", BuyScreen),
            ("sell", SellScreen),
        ]:
            frame = cls(self)
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            self._screens[name] = frame

    def _show(self, name: str) -> None:
        screen = self._screens[name]
        screen.tkraise()
        screen.on_show()

    def show_home(self) -> None:
        self._show("home")

    def show_buy(self) -> None:
        self._show("buy")

    def show_sell(self) -> None:
        self._show("sell")

    # ------------------------------------------------------------------

    def _on_close(self) -> None:
        self._sync.stop()
        self.destroy()


def main() -> None:
    app = KioskApp()
    app.mainloop()


if __name__ == "__main__":
    main()
