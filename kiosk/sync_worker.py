"""Background sync worker.

Runs in a daemon thread: reads unsent events from the local SQLite
``event_queue`` table and POSTs them to the backend API.  Retries on failure
using simple exponential back-off up to ``max_retry_delay``.
"""
from __future__ import annotations

import json
import logging
import threading
import time

from kiosk.api_client import ApiClient
from kiosk.db import connect, get_pending_events, mark_event_sent

logger = logging.getLogger(__name__)


class SyncWorker(threading.Thread):
    def __init__(
        self,
        api: ApiClient,
        poll_interval: float = 5.0,
        max_retry_delay: float = 60.0,
    ) -> None:
        super().__init__(daemon=True, name="sync-worker")
        self._api = api
        self._poll_interval = poll_interval
        self._max_retry_delay = max_retry_delay
        self._stop_event = threading.Event()

    def stop(self) -> None:
        self._stop_event.set()

    def run(self) -> None:
        retry_delay = self._poll_interval
        while not self._stop_event.is_set():
            try:
                self._flush()
                retry_delay = self._poll_interval
            except Exception as exc:
                logger.warning("Sync worker error: %s – retrying in %.0fs", exc, retry_delay)
                retry_delay = min(retry_delay * 2, self._max_retry_delay)
            self._stop_event.wait(retry_delay)

    def _flush(self) -> None:
        conn = connect()
        try:
            pending = get_pending_events(conn)
            for row in pending:
                try:
                    payload = json.loads(row["payload_json"])
                    self._api.record_event(
                        tx_id=row["tx_id"],
                        event_type=row["event_type"],
                        payload=payload,
                    )
                    mark_event_sent(conn, row["id"])
                    logger.debug(
                        "Flushed event %d (%s) for tx %s",
                        row["id"],
                        row["event_type"],
                        row["tx_id"],
                    )
                except Exception as exc:
                    logger.warning(
                        "Failed to send event %d: %s", row["id"], exc
                    )
                    # Leave unsent; will retry on next cycle
        finally:
            conn.close()
