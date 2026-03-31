import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "backend.sqlite3"


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db() -> None:
    conn = connect()
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            tx_id           TEXT PRIMARY KEY,
            status          TEXT NOT NULL,
            side            TEXT NOT NULL,
            asset           TEXT NOT NULL,
            fiat            TEXT NOT NULL,
            fiat_amount     INTEGER NOT NULL,
            payout_address  TEXT,
            idempotency_key TEXT NOT NULL UNIQUE,
            created_at_utc  TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_tx_idem
            ON transactions(idempotency_key);

        CREATE TABLE IF NOT EXISTS tx_events (
            event_id        TEXT PRIMARY KEY,
            tx_id           TEXT NOT NULL,
            event_type      TEXT NOT NULL,
            payload_json    TEXT NOT NULL DEFAULT '{}',
            recorded_at_utc TEXT NOT NULL,
            FOREIGN KEY (tx_id) REFERENCES transactions(tx_id)
        );

        CREATE INDEX IF NOT EXISTS idx_tx_events_tx_id
            ON tx_events(tx_id);
        """
    )
    conn.commit()
    conn.close()
