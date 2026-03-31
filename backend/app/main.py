from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI

from backend.app.db import init_db
from backend.app.routers.transactions import router as tx_router
from shared.models import Health


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Crypto Teller Machine – Backend API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(tx_router)


@app.get("/v1/health", response_model=Health)
def health() -> Health:
    return Health(status="ok", time_utc=datetime.now(timezone.utc))
