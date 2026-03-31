"""Local SQLite database for kiosk-side state management.

Tables:
- ``local_tx``   – transaction state-machine checkpoints.
- ``event_queue`` – events waiting to be flushed to the backend API.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "kiosk.sqlite3"


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db() -> None:
    conn = connect()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS local_tx (
            tx_id          TEXT PRIMARY KEY,
            status         TEXT NOT NULL,
            side           TEXT NOT NULL,
            fiat_amount    INTEGER NOT NULL,
            asset_amount   TEXT,
            created_at_utc TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS event_queue (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            tx_id          TEXT NOT NULL,
            event_type     TEXT NOT NULL,
            payload_json   TEXT NOT NULL DEFAULT '{}',
            created_at_utc TEXT NOT NULL,
            sent           INTEGER NOT NULL DEFAULT 0
        );
        """
    )
    conn.commit()
    conn.close()


def upsert_local_tx(
    conn: sqlite3.Connection,
    tx_id: str,
    status: str,
    side: str,
    fiat_amount: int,
    asset_amount: str = "",
    created_at_utc: str = "",
) -> None:
    conn.execute(
        """
        INSERT INTO local_tx (tx_id, status, side, fiat_amount, asset_amount, created_at_utc)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(tx_id) DO UPDATE SET status=excluded.status,
                                          asset_amount=excluded.asset_amount
        """,
        (tx_id, status, side, fiat_amount, asset_amount, created_at_utc),
    )
    conn.commit()


def enqueue_event(
    conn: sqlite3.Connection,
    tx_id: str,
    event_type: str,
    payload_json: str = "{}",
) -> None:
    from datetime import datetime, timezone

    conn.execute(
        """
        INSERT INTO event_queue (tx_id, event_type, payload_json, created_at_utc)
        VALUES (?, ?, ?, ?)
        """,
        (tx_id, event_type, payload_json, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()


def get_pending_events(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM event_queue WHERE sent = 0 ORDER BY id ASC"
    ).fetchall()


def mark_event_sent(conn: sqlite3.Connection, event_id: int) -> None:
    conn.execute("UPDATE event_queue SET sent = 1 WHERE id = ?", (event_id,))
    conn.commit()
