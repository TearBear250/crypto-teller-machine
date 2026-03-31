"""
XRP chain plugin — placeholder

Implements the ChainPlugin interface for XRP (XRP Ledger).
IMPORTANT: XRP transactions often require a destination tag. The kiosk UI must
prompt the user to provide one when required.

Currently returns stub data. Replace with real xrpl-py calls.
"""

import os
import logging

log = logging.getLogger("chain-plugin.xrp")

ASSET_ID = "xrp"
NETWORK_MODE = "testnet" if os.environ.get("CTM_CHAIN_TESTNET", "true").lower() == "true" else "mainnet"
REQUIRES_DESTINATION_TAG = True


def validate_address(address: str) -> dict:
    # XRP classic address starts with 'r', X-address starts with 'X'
    ok = address.startswith(("r", "X")) and len(address) >= 25
    warnings = [] if ok else ["Address format not recognized for XRP"]
    if ok and REQUIRES_DESTINATION_TAG:
        warnings.append("Destination tag may be required for exchange addresses")
    return {"ok": ok, "normalized": address.strip(), "warnings": warnings}


def get_quote(fiat_amount: float, fiat_currency: str = "CAD") -> dict:
    stub_rate = 0.72  # 1 XRP = 0.72 CAD (placeholder)
    fee_pct = 0.02
    fee_fiat = round(fiat_amount * fee_pct, 2)
    net_fiat = fiat_amount - fee_fiat
    asset_amount = round(net_fiat / stub_rate, 6)
    return {"asset_amount": asset_amount, "rate": stub_rate, "fee_fiat": fee_fiat}


def build_payout_tx(destination: str, amount: float, destination_tag: "int | None" = None) -> dict:
    log.warning("build_payout_tx: placeholder")
    tx = {"asset_id": ASSET_ID, "destination": destination, "amount": amount, "raw_tx": "PLACEHOLDER"}
    if destination_tag is not None:
        tx["destination_tag"] = destination_tag
    return tx


def broadcast_tx(tx: dict) -> str:
    log.warning("broadcast_tx: placeholder")
    return "PLACEHOLDER_TXID_XRP"


def track_tx(txid: str) -> dict:
    # XRP uses ledger finality, not block confirmations
    return {"txid": txid, "state": "CONFIRMING", "confirmations": 0, "validated": False}


def required_confirmations(fiat_amount: float) -> int:
    # XRP: 1 validated ledger close is effectively final
    return 1
