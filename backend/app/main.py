from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .ai_service import generate_triage_recommendation
from .config import settings
from .models import ValidationError, parse_consent, parse_preference, parse_triage_request
from .security import authenticate_user, create_access_token, verify_access_token
from .store import audit_store, consent_store, preference_store


JsonResponse = tuple[int, bytes]


def _json(status: int, payload: dict[str, Any]) -> JsonResponse:
    return status, json.dumps(payload, separators=(",", ":")).encode()


def _load_json(body: bytes) -> dict[str, Any]:
    try:
        parsed = json.loads(body or b"{}")
    except json.JSONDecodeError as exc:
        raise ValidationError("invalid JSON payload") from exc
    if not isinstance(parsed, dict):
        raise ValidationError("JSON payload must be an object")
    return parsed


def _append_audit(event: dict[str, Any]) -> None:
    data = audit_store.load([])
    data.append(event)
    audit_store.save(data[-5000:])


def _residency_allowed(country: str) -> bool:
    return country in settings.allowed_data_countries


def handle_request(method: str, path: str, headers: dict[str, str], body: bytes) -> JsonResponse:
    if method == "GET" and path == "/health":
        return _json(
            200,
            {
                "status": "ok",
                "service": settings.app_name,
                "version": settings.api_version,
                "deployment_country": settings.deployment_country,
                "offline_ready": True,
            },
        )

    if method == "GET" and path == "/api/privacy/policy":
        return _json(
            200,
            {
                "data_residency": {
                    "deployment_country": settings.deployment_country,
                    "allowed_storage_countries": list(settings.allowed_data_countries),
                    "cross_border_transfer": "disabled",
                },
                "data_sharing": "No external big-tech data sharing is permitted by policy.",
                "consent_required": True,
            },
        )

    if method == "POST" and path == "/auth/token":
        try:
            data = _load_json(body)
        except ValidationError as exc:
            return _json(400, {"detail": str(exc)})

        user = authenticate_user(str(data.get("username", "")), str(data.get("password", "")))
        if not user:
            return _json(401, {"detail": "Invalid credentials"})

        token = create_access_token(user["username"], user["role"])
        return _json(200, {"access_token": token, "token_type": "bearer"})

    if method == "POST" and path == "/api/consent":
        try:
            payload = parse_consent(_load_json(body))
        except ValidationError as exc:
            return _json(400, {"detail": str(exc)})

        data = consent_store.load({})
        data[payload.patient_id] = {
            "data_processing": payload.data_processing,
            "ai_assistance": payload.ai_assistance,
            "emergency_override": payload.emergency_override,
        }
        consent_store.save(data)
        return _json(200, {"status": "saved", "patient_id": payload.patient_id})

    if method == "POST" and path == "/api/preferences":
        try:
            payload = parse_preference(_load_json(body))
        except ValidationError as exc:
            return _json(400, {"detail": str(exc)})

        data = preference_store.load({})
        data[payload.user_id] = {"widgets": payload.widgets, "language": payload.language}
        preference_store.save(data)
        return _json(200, {"status": "saved", "user_id": payload.user_id})

    if method == "GET" and path.startswith("/api/preferences/"):
        user_id = path.rsplit("/", 1)[-1].strip()
        data = preference_store.load({})
        return _json(200, {"user_id": user_id, "preferences": data.get(user_id, {"widgets": [], "language": "en"})})

    if method == "POST" and path == "/api/triage":
        auth = headers.get("authorization", "")
        if not auth.startswith("Bearer "):
            return _json(401, {"detail": "Missing bearer token"})

        try:
            claims = verify_access_token(auth.split(" ", 1)[1])
            request = parse_triage_request(_load_json(body))
        except ValidationError as exc:
            return _json(400, {"detail": str(exc)})
        except ValueError:
            return _json(401, {"detail": "Invalid token"})

        if not _residency_allowed(request.country):
            return _json(403, {"detail": "Data residency policy blocks processing in this country"})

        consent_data = consent_store.load({}).get(request.patient_id, {})
        if not consent_data.get("data_processing"):
            return _json(403, {"detail": "Patient consent for data processing is required"})

        result = generate_triage_recommendation(request)
        _append_audit(
            {
                "event": "triage_generated",
                "patient_id": request.patient_id,
                "urgency": result.get("urgency"),
                "country": request.country,
                "requested_by": claims.get("sub"),
            }
        )
        return _json(200, result)

    return _json(404, {"detail": "Not found"})


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _read_body(self) -> bytes:
        length = int(self.headers.get("Content-Length", "0"))
        return self.rfile.read(length) if length else b""

    def _send_json(self, status: int, payload: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:  # noqa: N802
        status, payload = handle_request("GET", self.path, {k.lower(): v for k, v in self.headers.items()}, b"")
        self._send_json(status, payload)

    def do_POST(self) -> None:  # noqa: N802
        status, payload = handle_request(
            "POST", self.path, {k.lower(): v for k, v in self.headers.items()}, self._read_body()
        )
        self._send_json(status, payload)


def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    run_server()
