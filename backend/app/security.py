from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time

SECRET = os.environ.get("AH_JWT_SECRET", "change-me-in-production")


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(data: str) -> bytes:
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode())


def hash_password(password: str) -> str:
    salt = b"ah-static-salt"
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000).hex()


FAKE_USERS = {
    "clinician": {
        "username": "clinician",
        "hashed_password": hash_password("SecurePass123!"),
        "role": "clinician",
    }
}


def authenticate_user(username: str, password: str) -> dict | None:
    user = FAKE_USERS.get(username)
    if not user:
        return None
    return user if hmac.compare_digest(user["hashed_password"], hash_password(password)) else None


def create_access_token(subject: str, role: str, ttl_minutes: int = 30) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"sub": subject, "role": role, "exp": int(time.time()) + ttl_minutes * 60}
    parts = [_b64url(json.dumps(header, separators=(",", ":")).encode()), _b64url(json.dumps(payload, separators=(",", ":")).encode())]
    signature = hmac.new(SECRET.encode(), ".".join(parts).encode(), hashlib.sha256).digest()
    return ".".join(parts + [_b64url(signature)])


def verify_access_token(token: str) -> dict:
    try:
        header_b64, payload_b64, sig_b64 = token.split(".")
        expected = hmac.new(SECRET.encode(), f"{header_b64}.{payload_b64}".encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(expected, _b64url_decode(sig_b64)):
            raise ValueError("invalid signature")
        payload = json.loads(_b64url_decode(payload_b64))
        if int(payload.get("exp", 0)) < int(time.time()):
            raise ValueError("token expired")
        return payload
    except Exception as exc:  # noqa: BLE001
        raise ValueError("invalid token") from exc
