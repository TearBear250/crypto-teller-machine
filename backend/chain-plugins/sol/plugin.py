"""
Solana chain plugin — placeholder

Implements the ChainPlugin interface for Solana (SOL).
Targets Solana devnet initially (set CHAIN_RPC_SOL in environment).

Currently returns stub data. Replace with real solana-py / solders calls.
"""

import os
import logging

log = logging.getLogger("chain-plugin.sol")

ASSET_ID = "sol"
NETWORK_MODE = "devnet" if os.environ.get("CTM_CHAIN_TESTNET", "true").lower() == "true" else "mainnet-beta"


def validate_address(address: str) -> dict:
    # Solana base58 public keys are 32–44 characters
    ok = len(address) >= 32 and len(address) <= 44
    return {
        "ok": ok,
        "normalized": address.strip(),
        "warnings": [] if ok else ["Address format not recognized for SOL"],
    }


def get_quote(fiat_amount: float, fiat_currency: str = "CAD") -> dict:
    stub_rate = 180.0  # 1 SOL = 180 CAD (placeholder)
    fee_pct = 0.02
    fee_fiat = round(fiat_amount * fee_pct, 2)
    net_fiat = fiat_amount - fee_fiat
    asset_amount = round(net_fiat / stub_rate, 9)
    return {"asset_amount": asset_amount, "rate": stub_rate, "fee_fiat": fee_fiat}


def build_payout_tx(destination: str, amount: float) -> dict:
    log.warning("build_payout_tx: placeholder")
    return {"asset_id": ASSET_ID, "destination": destination, "amount": amount, "raw_tx": "PLACEHOLDER"}


def broadcast_tx(tx: dict) -> str:
    log.warning("broadcast_tx: placeholder")
    return "PLACEHOLDER_TXID_SOL"


def track_tx(txid: str) -> dict:
    # Solana uses slot finality
    return {"txid": txid, "state": "CONFIRMING", "confirmations": 0, "finalized": False}


def required_confirmations(fiat_amount: float) -> int:
    # Solana: finalized slot is effectively instant for small amounts
    return 1
