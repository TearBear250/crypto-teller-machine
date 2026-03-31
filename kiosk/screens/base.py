"""Tkinter screen base class and shared UI helpers."""
from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kiosk.app import KioskApp

FONT_TITLE = ("Arial", 36, "bold")
FONT_BODY = ("Arial", 24)
FONT_BTN = ("Arial", 28, "bold")
FONT_SMALL = ("Arial", 18)

BTN_PADX = 30
BTN_PADY = 20
BTN_WIDTH = 18

BG = "#1a1a2e"        # dark navy
FG = "#eaeaea"        # light grey
ACCENT = "#e94560"    # red-pink
ACCENT2 = "#0f3460"   # mid-navy
SUCCESS = "#16c79a"   # teal


def styled_button(
    parent,
    text: str,
    command,
    bg: str = ACCENT,
    fg: str = "#ffffff",
    width: int = BTN_WIDTH,
) -> tk.Button:
    return tk.Button(
        parent,
        text=text,
        command=command,
        font=FONT_BTN,
        bg=bg,
        fg=fg,
        activebackground=fg,
        activeforeground=bg,
        relief=tk.FLAT,
        width=width,
        padx=BTN_PADX,
        pady=BTN_PADY,
        cursor="hand2",
    )


class BaseScreen(tk.Frame):
    """Every kiosk screen extends this.  ``app`` is the root KioskApp."""

    def __init__(self, app: "KioskApp") -> None:
        super().__init__(app, bg=BG)
        self.app = app
        self.build()

    def build(self) -> None:
        """Subclasses override this to populate the frame."""

    def on_show(self) -> None:
        """Called each time this screen becomes visible."""

    def _title(self, text: str) -> tk.Label:
        lbl = tk.Label(self, text=text, font=FONT_TITLE, bg=BG, fg=FG)
        lbl.pack(pady=(40, 20))
        return lbl

    def _label(self, text: str, fg: str = FG) -> tk.Label:
        lbl = tk.Label(self, text=text, font=FONT_BODY, bg=BG, fg=fg)
        lbl.pack(pady=8)
        return lbl

    def _back_button(self) -> None:
        styled_button(
            self,
            text="← Back",
            command=self.app.show_home,
            bg=ACCENT2,
        ).pack(pady=(20, 10))
