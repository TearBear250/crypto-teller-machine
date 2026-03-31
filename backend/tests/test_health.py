"""Unit tests for the /v1/health endpoint."""
from __future__ import annotations


def test_health_returns_ok(client):
    resp = client.get("/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "time_utc" in data


def test_health_time_utc_is_iso8601(client):
    from datetime import datetime

    resp = client.get("/v1/health")
    data = resp.json()
    # Should parse without raising
    dt = datetime.fromisoformat(data["time_utc"].replace("Z", "+00:00"))
    assert dt is not None
