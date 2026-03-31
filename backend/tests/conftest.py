"""Pytest configuration – sets up a temporary in-memory (or temp-file) SQLite
database so tests do not interfere with each other or with a local dev DB."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Point the backend DB at a temp file before importing the app
_tmp_db = tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False)
_tmp_db.close()

import backend.app.db as _db_module

_db_module.DB_PATH = Path(_tmp_db.name)

from backend.app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client() -> TestClient:
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def _reset_db():
    """Re-create tables before each test so tests are isolated."""
    _db_module.init_db()
    yield
    # Clean up rows after each test
    conn = _db_module.connect()
    conn.execute("DELETE FROM tx_events")
    conn.execute("DELETE FROM transactions")
    conn.commit()
    conn.close()
