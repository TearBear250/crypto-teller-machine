#!/usr/bin/env python3
"""
backend-api — placeholder / hello-service

Minimal skeleton implementing the /v1/health endpoint from the OpenAPI spec at
shared/contracts/openapi.yaml. Replace with full implementation.

Run with:
    python3 main.py

Or via Podman (see ../README.md for instructions).
"""

import os
import json
import logging
import ssl
from http.server import BaseHTTPRequestHandler, HTTPServer

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "info").upper(),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("backend-api")


def build_health() -> dict:
    return {
        "status": "ok",
        "version": "0.1.0-placeholder",
        "service": "backend-api",
        "testnet": os.environ.get("CTM_CHAIN_TESTNET", "false").lower() == "true",
        "note": "Placeholder — replace with full backend-api implementation",
    }


ROUTES = {
    "GET /v1/health": lambda: (200, build_health()),
    "GET /v1/assets": lambda: (
        200,
        {
            "assets": [
                {"id": "ltc", "name": "Litecoin", "enabled": True, "network_mode": "testnet"},
                {"id": "doge", "name": "Dogecoin", "enabled": True, "network_mode": "testnet"},
                {"id": "xrp", "name": "XRP", "enabled": False, "network_mode": "testnet"},
                {"id": "sol", "name": "Solana", "enabled": False, "network_mode": "testnet"},
            ]
        },
    ),
}


class ApiHandler(BaseHTTPRequestHandler):
    def _dispatch(self, method: str):
        key = f"{method} {self.path}"
        if key in ROUTES:
            status, body = ROUTES[key]()
        else:
            status, body = 404, {"error": {"code": "NOT_FOUND", "message": "Not found"}}
        encoded = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):  # noqa: N802
        self._dispatch("GET")

    def do_POST(self):  # noqa: N802
        self._dispatch("POST")

    def log_message(self, fmt, *args):  # noqa: N802
        log.info(fmt, *args)


def main():
    host = "0.0.0.0"
    port = int(os.environ.get("API_PORT", "8443"))

    server = HTTPServer((host, port), ApiHandler)

    cert = os.environ.get("TLS_CERT_PATH")
    key = os.environ.get("TLS_KEY_PATH")
    ca = os.environ.get("TLS_CA_PATH")

    if cert and key and ca and os.path.exists(cert):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        ctx.load_cert_chain(cert, key)
        ctx.load_verify_locations(ca)
        ctx.verify_mode = ssl.CERT_REQUIRED
        server.socket = ctx.wrap_socket(server.socket, server_side=True)
        log.info("TLS enabled (mTLS required, minimum TLS 1.2)")
    else:
        log.warning(
            "TLS certificates not found — running in plain HTTP mode (development only)"
        )

    log.info("backend-api starting on %s:%d", host, port)
    log.info("health: %s", json.dumps(build_health(), indent=2))
    log.info("Listening — GET /v1/health to check status. Ctrl-C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("backend-api shutting down")


if __name__ == "__main__":
    main()
