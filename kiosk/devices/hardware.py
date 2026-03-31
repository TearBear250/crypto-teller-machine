"""Device abstraction interfaces for kiosk hardware.

Each class defines the contract that a real hardware driver must satisfy.
The simulator implementations allow full end-to-end development without
physical hardware.  When real devices arrive, implement the abstract base
classes using the vendor's official SDK and swap them in via dependency
injection in ``kiosk/app.py``.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Optional


class CashAcceptor(ABC):
    """Abstract interface for a bill-acceptor (cash-in) device."""

    @abstractmethod
    def start_accepting(self) -> None:
        """Enable the cash slot; begin accepting bills."""

    @abstractmethod
    def stop_accepting(self) -> None:
        """Disable the cash slot; reject further bills."""

    @abstractmethod
    def get_inserted_cents(self) -> int:
        """Return total cash inserted since last reset, in cents."""

    @abstractmethod
    def reset(self) -> None:
        """Reset the inserted amount counter."""


class CashDispenser(ABC):
    """Abstract interface for a cash-dispenser (cash-out) device."""

    @abstractmethod
    def dispense(self, amount_cents: int) -> bool:
        """Dispense *amount_cents* worth of cash.

        Returns ``True`` on success, ``False`` if unable to dispense
        (e.g. insufficient notes loaded).
        """

    @abstractmethod
    def get_cassette_level_cents(self) -> int:
        """Return estimated cash level remaining in dispenser, in cents."""


class ReceiptPrinter(ABC):
    """Abstract interface for a receipt printer."""

    @abstractmethod
    def print_receipt(self, lines: list[str]) -> bool:
        """Print *lines* as a receipt.  Returns ``True`` on success."""


# ---------------------------------------------------------------------------
# Simulator implementations (for development / testing)
# ---------------------------------------------------------------------------

class SimulatedCashAcceptor(CashAcceptor):
    """Simulated bill acceptor; ``simulate_insert`` mimics a bill drop."""

    def __init__(self) -> None:
        self._accepting = False
        self._inserted_cents = 0
        self._on_insert: Optional[Callable[[int], None]] = None

    def start_accepting(self) -> None:
        self._accepting = True

    def stop_accepting(self) -> None:
        self._accepting = False

    def get_inserted_cents(self) -> int:
        return self._inserted_cents

    def reset(self) -> None:
        self._inserted_cents = 0

    def set_on_insert_callback(self, cb: Callable[[int], None]) -> None:
        """Register a callback invoked when cash is simulated-inserted."""
        self._on_insert = cb

    def simulate_insert(self, amount_cents: int) -> None:
        """Called by the UI's 'Insert Cash' button to simulate a bill drop."""
        if self._accepting:
            self._inserted_cents += amount_cents
            if self._on_insert:
                self._on_insert(amount_cents)


class SimulatedCashDispenser(CashDispenser):
    """Simulated cash dispenser with a configurable cassette level."""

    def __init__(self, initial_level_cents: int = 1_000_000) -> None:
        self._level_cents = initial_level_cents

    def dispense(self, amount_cents: int) -> bool:
        if amount_cents > self._level_cents:
            return False
        self._level_cents -= amount_cents
        return True

    def get_cassette_level_cents(self) -> int:
        return self._level_cents


class SimulatedReceiptPrinter(ReceiptPrinter):
    """Simulated receipt printer that writes to stdout."""

    def print_receipt(self, lines: list[str]) -> bool:
        print("--- RECEIPT ---")
        for line in lines:
            print(line)
        print("---------------")
        return True
