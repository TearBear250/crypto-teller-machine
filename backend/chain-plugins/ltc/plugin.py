"""
Litecoin chain plugin — placeholder

Implements the ChainPlugin interface for Litecoin (LTC).
Currently returns stub data. Replace with real litecoin-python / RPC calls.

Testnet RPC: http://localhost:19332 (set CHAIN_RPC_LTC in environment)
"""

import os
import logging

log = logging.getLogger("chain-plugin.ltc")

ASSET_ID = "ltc"
NETWORK_MODE = "testnet" if os.environ.get("CTM_CHAIN_TESTNET", "true").lower() == "true" else "mainnet"


def validate_address(address: str) -> dict:
    """Validate a Litecoin address."""
    # TODO: Use python-litecoin or local node RPC to validate
    ok = address.startswith(("m", "n", "Q", "M", "ltc1")) and len(address) >= 26
    return {
        "ok": ok,
        "normalized": address.strip(),
        "warnings": [] if ok else ["Address format not recognized for LTC"],
    }


def get_quote(fiat_amount: float, fiat_currency: str = "CAD") -> dict:
    """Return a stub quote for testing."""
    # TODO: Fetch real rate from price oracle or exchange API
    stub_rate = 90.0  # 1 LTC = 90 CAD (placeholder)
    fee_pct = 0.02
    fee_fiat = round(fiat_amount * fee_pct, 2)
    net_fiat = fiat_amount - fee_fiat
    asset_amount = round(net_fiat / stub_rate, 8)
    return {
        "asset_amount": asset_amount,
        "rate": stub_rate,
        "fee_fiat": fee_fiat,
    }


def build_payout_tx(destination: str, amount: float) -> dict:
    """Build a placeholder payout transaction."""
    # TODO: Use Litecoin RPC createrawtransaction / signrawtransaction
    log.warning("build_payout_tx: placeholder — not broadcasting real transaction")
    return {
        "asset_id": ASSET_ID,
        "destination": destination,
        "amount": amount,
        "raw_tx": "PLACEHOLDER_RAW_TX",
    }


def broadcast_tx(tx: dict) -> str:
    """Broadcast a transaction to the network."""
    # TODO: Use Litecoin RPC sendrawtransaction
    log.warning("broadcast_tx: placeholder — returning fake txid")
    return "PLACEHOLDER_TXID_LTC"


def track_tx(txid: str) -> dict:
    """Track a transaction's confirmation status."""
    # TODO: Use Litecoin RPC gettransaction
    return {
        "txid": txid,
        "state": "CONFIRMING",
        "confirmations": 0,
        "block_height": None,
    }


def required_confirmations(fiat_amount: float) -> int:
    """Return minimum required confirmations based on fiat amount.
    0-conf is not used; minimum is 1 to mitigate double-spend/RBF risk.
    """
    if fiat_amount <= 50:
        return 1
    if fiat_amount <= 500:
        return 2
    return 3
