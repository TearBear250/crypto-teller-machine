#!/usr/bin/env python3
"""
ltm-hal simulator

Simulates hardware events (bill acceptor, cash dispenser, QR scanner, receipt printer)
for use during development and CI when no physical devices are present.

Usage:
    CTM_HAL_SIMULATE=true python3 simulator.py

Events are printed to stdout as JSON; the kiosk-agent consumes them via the HAL
interface (to be implemented).
"""

import json
import logging
import os
import time

log = logging.getLogger("ltm-hal.simulator")


class SimulatedBillAcceptor:
    """Simulates a bill acceptor/validator (MDB protocol)."""

    def insert_bill(self, denomination: int, currency: str = "CAD") -> dict:
        event = {
            "source": "bill_acceptor",
            "event": "BILL_INSERTED",
            "denomination": denomination,
            "currency": currency,
            "timestamp": time.time(),
        }
        log.info("HAL simulator: %s", json.dumps(event))
        return event

    def reject_bill(self, denomination: int, reason: str = "VALIDATION_FAILED") -> dict:
        event = {
            "source": "bill_acceptor",
            "event": "BILL_REJECTED",
            "denomination": denomination,
            "reason": reason,
            "timestamp": time.time(),
        }
        log.info("HAL simulator: %s", json.dumps(event))
        return event


class SimulatedCashDispenser:
    """Simulates a cash dispenser cassette."""

    def dispense(self, amount: int, currency: str = "CAD") -> dict:
        event = {
            "source": "cash_dispenser",
            "event": "CASH_DISPENSED",
            "amount": amount,
            "currency": currency,
            "timestamp": time.time(),
        }
        log.info("HAL simulator: %s", json.dumps(event))
        return event


class SimulatedQRScanner:
    """Simulates a QR code / camera scanner."""

    def scan(self, address: str) -> dict:
        event = {
            "source": "qr_scanner",
            "event": "QR_SCANNED",
            "value": address,
            "timestamp": time.time(),
        }
        log.info("HAL simulator: %s", json.dumps(event))
        return event


class SimulatedPrinter:
    """Simulates a receipt printer."""

    def print_receipt(self, lines: list) -> dict:
        event = {
            "source": "printer",
            "event": "RECEIPT_PRINTED",
            "lines": lines,
            "timestamp": time.time(),
        }
        log.info("HAL simulator: %s", json.dumps(event))
        return event


if __name__ == "__main__":
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "info").upper())
    log.info("HAL simulator running (demo sequence)")

    acceptor = SimulatedBillAcceptor()
    dispenser = SimulatedCashDispenser()
    scanner = SimulatedQRScanner()
    printer = SimulatedPrinter()

    print(json.dumps(acceptor.insert_bill(20), indent=2))
    print(json.dumps(scanner.scan("LTC_testnet_address_placeholder"), indent=2))
    print(json.dumps(printer.print_receipt(["Thank you", "Txid: PLACEHOLDER"]), indent=2))
