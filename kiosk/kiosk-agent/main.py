#!/usr/bin/env python3
"""
kiosk-agent — placeholder / hello-service

This is a minimal skeleton that verifies the container and environment are working.
Replace with the full transaction state machine implementation.

Run with:
    python3 main.py

Or via Podman (see ../README.md for instructions).
"""

import os
import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "info").upper(),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("kiosk-agent")


def build_status() -> dict:
    return {
        "service": "kiosk-agent",
        "status": "ok",
        "kiosk_id": os.environ.get("KIOSK_ID", "unknown"),
        "backend_url": os.environ.get("BACKEND_URL", "not-configured"),
        "hal_simulate": os.environ.get("CTM_HAL_SIMULATE", "false").lower() == "true",
        "testnet": os.environ.get("CTM_CHAIN_TESTNET", "false").lower() == "true",
        "note": "Placeholder — replace with full kiosk-agent implementation",
    }


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        if self.path == "/health":
            body = json.dumps(build_status()).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, fmt, *args):  # noqa: N802
        log.info(fmt, *args)


def main():
    host = "0.0.0.0"  # Must bind to 0.0.0.0 inside container; the systemd unit
    # publishes only on 127.0.0.1 on the host (--publish 127.0.0.1:8080:8080).
    port = int(os.environ.get("HEALTH_PORT", "8080"))
    log.info("kiosk-agent starting on %s:%d", host, port)
    log.info("status: %s", json.dumps(build_status(), indent=2))
    server = HTTPServer((host, port), HealthHandler)
    log.info("Listening — GET /health to check status. Ctrl-C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("kiosk-agent shutting down")


if __name__ == "__main__":
    main()
