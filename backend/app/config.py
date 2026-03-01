from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str
    api_version: str
    access_token_expire_minutes: int
    jwt_secret: str
    blocked_phrases: tuple[str, ...]
    deployment_country: str
    allowed_data_countries: tuple[str, ...]
    storage_dir: str


settings = Settings(
    app_name=os.environ.get("AH_APP_NAME", "Africa Healthcare Platform"),
    api_version=os.environ.get("AH_API_VERSION", "v1"),
    access_token_expire_minutes=int(os.environ.get("AH_TOKEN_TTL_MIN", "30")),
    jwt_secret=os.environ.get("AH_JWT_SECRET", "change-me-in-production"),
    blocked_phrases=tuple(
        phrase.strip().lower()
        for phrase in os.environ.get(
            "AH_BLOCKED_PHRASES",
            "self-harm instruction,illegal drug dosage,bypass diagnosis protocol",
        ).split(",")
        if phrase.strip()
    ),
    deployment_country=os.environ.get("AH_DEPLOYMENT_COUNTRY", "Rwanda"),
    allowed_data_countries=tuple(
        c.strip() for c in os.environ.get("AH_ALLOWED_DATA_COUNTRIES", "Rwanda").split(",") if c.strip()
    ),
    storage_dir=os.environ.get("AH_STORAGE_DIR", "./backend_data"),
)
