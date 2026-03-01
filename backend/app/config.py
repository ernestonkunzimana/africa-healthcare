from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Africa Healthcare Platform"
    api_version: str = "v1"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    ai_max_tokens: int = 512
    ai_blocked_phrases: tuple[str, ...] = (
        "self-harm instruction",
        "illegal drug dosage",
        "bypass diagnosis protocol",
    )


settings = Settings()
