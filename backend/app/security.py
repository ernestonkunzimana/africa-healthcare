from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import TypedDict

from .config import settings


class UserRecord(TypedDict):
    username: str
    salt: str
    hashed_password: str
    role: str


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode())


def hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000).hex()


def _new_user(username: str, password: str, role: str) -> UserRecord:
    salt = secrets.token_hex(16)
    return {
        "username": username,
        "salt": salt,
        "hashed_password": hash_password(password, salt),
        "role": role,
    }


FAKE_USERS: dict[str, UserRecord] = {
    "clinician": _new_user("clinician", "SecurePass123!", "clinician"),
}


def authenticate_user(username: str, password: str) -> UserRecord | None:
    user = FAKE_USERS.get(username)
    if not user:
        return None
    attempted_hash = hash_password(password, user["salt"])
    if not hmac.compare_digest(user["hashed_password"], attempted_hash):
        return None
    return user


def create_access_token(subject: str, role: str, ttl_minutes: int | None = None) -> str:
    ttl = ttl_minutes if ttl_minutes is not None else settings.access_token_expire_minutes
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"sub": subject, "role": role, "exp": int(time.time()) + ttl * 60}
    encoded_header = _b64url(json.dumps(header, separators=(",", ":")).encode())
    encoded_payload = _b64url(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{encoded_header}.{encoded_payload}".encode()
    signature = hmac.new(settings.jwt_secret.encode(), signing_input, hashlib.sha256).digest()
    return f"{encoded_header}.{encoded_payload}.{_b64url(signature)}"


def verify_access_token(token: str) -> dict:
    try:
        encoded_header, encoded_payload, encoded_signature = token.split(".")
        signing_input = f"{encoded_header}.{encoded_payload}".encode()
        expected_signature = hmac.new(
            settings.jwt_secret.encode(), signing_input, hashlib.sha256
        ).digest()
        provided_signature = _b64url_decode(encoded_signature)
        if not hmac.compare_digest(expected_signature, provided_signature):
            raise ValueError("invalid signature")

        payload = json.loads(_b64url_decode(encoded_payload))
        if int(payload.get("exp", 0)) <= int(time.time()):
            raise ValueError("token expired")
        if not payload.get("sub") or not payload.get("role"):
            raise ValueError("missing required claims")
        return payload
    except Exception as exc:  # noqa: BLE001
        raise ValueError("invalid token") from exc
