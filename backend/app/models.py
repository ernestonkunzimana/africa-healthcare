from datetime import datetime
from pydantic import BaseModel, Field


class HealthSignal(BaseModel):
    heart_rate: int = Field(..., ge=30, le=220)
    spo2: int = Field(..., ge=50, le=100)
    systolic_bp: int = Field(..., ge=70, le=230)
    diastolic_bp: int = Field(..., ge=30, le=160)


class TriageRequest(BaseModel):
    patient_id: str = Field(..., min_length=3, max_length=64)
    symptoms: list[str] = Field(..., min_items=1, max_items=20)
    notes: str = Field(default="", max_length=2000)
    language: str = Field(default="en", max_length=10)
    health_signal: HealthSignal


class AlignmentMeta(BaseModel):
    risk_level: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    safety_checks: list[str]


class TriageResponse(BaseModel):
    recommendation: str
    urgency: str
    actions: list[str]
    alignment: AlignmentMeta
    generated_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserAuthRequest(BaseModel):
    username: str
    password: str
