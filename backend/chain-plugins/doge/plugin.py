"""
Dogecoin chain plugin — placeholder

Implements the ChainPlugin interface for Dogecoin (DOGE).
Currently returns stub data. Replace with real dogecoin RPC calls.
"""

import os
import logging

log = logging.getLogger("chain-plugin.doge")

ASSET_ID = "doge"
NETWORK_MODE = "testnet" if os.environ.get("CTM_CHAIN_TESTNET", "true").lower() == "true" else "mainnet"


def validate_address(address: str) -> dict:
    ok = address.startswith(("D", "n", "m")) and len(address) >= 26
    return {
        "ok": ok,
        "normalized": address.strip(),
        "warnings": [] if ok else ["Address format not recognized for DOGE"],
    }


def get_quote(fiat_amount: float, fiat_currency: str = "CAD") -> dict:
    stub_rate = 0.18  # 1 DOGE = 0.18 CAD (placeholder)
    fee_pct = 0.02
    fee_fiat = round(fiat_amount * fee_pct, 2)
    net_fiat = fiat_amount - fee_fiat
    asset_amount = round(net_fiat / stub_rate, 2)
    return {"asset_amount": asset_amount, "rate": stub_rate, "fee_fiat": fee_fiat}


def build_payout_tx(destination: str, amount: float) -> dict:
    log.warning("build_payout_tx: placeholder")
    return {"asset_id": ASSET_ID, "destination": destination, "amount": amount, "raw_tx": "PLACEHOLDER"}


def broadcast_tx(tx: dict) -> str:
    log.warning("broadcast_tx: placeholder")
    return "PLACEHOLDER_TXID_DOGE"


def track_tx(txid: str) -> dict:
    return {"txid": txid, "state": "CONFIRMING", "confirmations": 0, "block_height": None}


def required_confirmations(fiat_amount: float) -> int:
    if fiat_amount <= 50:
        return 1
    if fiat_amount <= 500:
        return 2
    return 3
