from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "Africa Healthcare Platform"
    api_version: str = "v1"
    access_token_expire_minutes: int = 30


settings = Settings()
