"""Home / attract screen."""
from __future__ import annotations

import tkinter as tk

from kiosk.screens.base import BaseScreen, BG, FG, ACCENT, ACCENT2, styled_button, FONT_TITLE, FONT_SMALL


class HomeScreen(BaseScreen):
    def build(self) -> None:
        self._title("₿ Crypto Teller Machine")
        self._label("Touch to begin", fg="#aaaaaa")

        tk.Frame(self, bg=BG, height=30).pack()

        styled_button(self, text="BUY Crypto  →", command=self.app.show_buy).pack(
            pady=15, ipadx=10, ipady=10
        )
        styled_button(
            self,
            text="SELL Crypto →",
            command=self.app.show_sell,
            bg=ACCENT2,
        ).pack(pady=15, ipadx=10, ipady=10)

        tk.Frame(self, bg=BG, height=40).pack()
        tk.Label(
            self,
            text="Rates are for demonstration only.\nNo real cash or crypto is exchanged.",
            font=FONT_SMALL,
            bg=BG,
            fg="#666688",
        ).pack()
