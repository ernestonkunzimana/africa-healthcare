from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .ai_service import generate_triage_recommendation
from .models import parse_triage_request
from .security import authenticate_user, create_access_token, verify_access_token


def _json(status: int, payload: dict) -> tuple[int, bytes]:
    return status, json.dumps(payload).encode()


def handle_request(method: str, path: str, headers: dict, body: bytes) -> tuple[int, bytes]:
    if method == "GET" and path == "/health":
        return _json(200, {"status": "ok", "service": "Africa Healthcare Platform"})

    if method == "POST" and path == "/auth/token":
        data = json.loads(body or b"{}")
        user = authenticate_user(data.get("username", ""), data.get("password", ""))
        if not user:
            return _json(401, {"detail": "Invalid credentials"})
        token = create_access_token(user["username"], user["role"])
        return _json(200, {"access_token": token, "token_type": "bearer"})

    if method == "POST" and path == "/api/triage":
        auth = headers.get("authorization", "")
        if not auth.startswith("Bearer "):
            return _json(401, {"detail": "Missing bearer token"})
        try:
            verify_access_token(auth.split(" ", 1)[1])
            req = parse_triage_request(json.loads(body or b"{}"))
        except ValueError as exc:
            return _json(400, {"detail": str(exc)})
        return _json(200, generate_triage_recommendation(req))

    return _json(404, {"detail": "Not found"})


class Handler(BaseHTTPRequestHandler):
    def _read_body(self) -> bytes:
        length = int(self.headers.get("Content-Length", "0"))
        return self.rfile.read(length) if length else b""

    def do_GET(self) -> None:  # noqa: N802
        status, payload = handle_request("GET", self.path, {k.lower(): v for k, v in self.headers.items()}, b"")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self) -> None:  # noqa: N802
        status, payload = handle_request("POST", self.path, {k.lower(): v for k, v in self.headers.items()}, self._read_body())
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(payload)


def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    run_server()
