"""HTTP client wrapper for the backend API."""
from __future__ import annotations

from typing import Optional

import requests

from shared.models import QuoteRequest, TxCreateRequest


class ApiClient:
    def __init__(self, base_url: str, timeout: int = 10) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def health(self) -> dict:
        r = requests.get(f"{self.base_url}/v1/health", timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def create_quote(self, req: QuoteRequest) -> dict:
        r = requests.post(
            f"{self.base_url}/v1/quotes",
            json=req.model_dump(),
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def create_tx(self, req: TxCreateRequest) -> dict:
        r = requests.post(
            f"{self.base_url}/v1/transactions",
            json=req.model_dump(),
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def get_tx(self, tx_id: str) -> dict:
        r = requests.get(
            f"{self.base_url}/v1/transactions/{tx_id}",
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def record_event(
        self,
        tx_id: str,
        event_type: str,
        payload: Optional[dict] = None,
    ) -> dict:
        body = {"event_type": event_type, "payload": payload or {}}
        r = requests.post(
            f"{self.base_url}/v1/transactions/{tx_id}/events",
            json=body,
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()
