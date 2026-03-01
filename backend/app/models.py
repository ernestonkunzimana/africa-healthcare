from __future__ import annotations

from dataclasses import dataclass


class ValidationError(ValueError):
    """Domain-level validation failure for incoming API payloads."""


@dataclass(frozen=True)
class HealthSignal:
    heart_rate: int
    spo2: int
    systolic_bp: int
    diastolic_bp: int


@dataclass(frozen=True)
class TriageRequest:
    patient_id: str
    symptoms: list[str]
    notes: str
    language: str
    country: str
    health_signal: HealthSignal


@dataclass(frozen=True)
class Consent:
    patient_id: str
    data_processing: bool
    ai_assistance: bool
    emergency_override: bool


@dataclass(frozen=True)
class Preference:
    user_id: str
    widgets: list[str]
    language: str


def _validate_range(name: str, value: int, lower: int, upper: int) -> None:
    if not (lower <= value <= upper):
        raise ValidationError(f"{name} must be between {lower} and {upper}")


def parse_triage_request(data: dict) -> TriageRequest:
    hs = data.get("health_signal") or {}
    try:
        request = TriageRequest(
            patient_id=str(data.get("patient_id", "")).strip(),
            symptoms=[str(s).strip() for s in data.get("symptoms", []) if str(s).strip()],
            notes=str(data.get("notes", "")).strip(),
            language=str(data.get("language", "en")).strip() or "en",
            country=str(data.get("country", "")).strip(),
            health_signal=HealthSignal(
                heart_rate=int(hs.get("heart_rate", 0)),
                spo2=int(hs.get("spo2", 0)),
                systolic_bp=int(hs.get("systolic_bp", 0)),
                diastolic_bp=int(hs.get("diastolic_bp", 0)),
            ),
        )
    except (TypeError, ValueError) as exc:
        raise ValidationError("invalid payload types") from exc

    if not (3 <= len(request.patient_id) <= 64):
        raise ValidationError("patient_id must be 3-64 chars")
    if not request.symptoms:
        raise ValidationError("at least one symptom is required")
    if len(request.symptoms) > 20:
        raise ValidationError("symptoms must be <= 20")
    if not request.country:
        raise ValidationError("country is required")

    _validate_range("heart_rate", request.health_signal.heart_rate, 30, 220)
    _validate_range("spo2", request.health_signal.spo2, 50, 100)
    _validate_range("systolic_bp", request.health_signal.systolic_bp, 70, 230)
    _validate_range("diastolic_bp", request.health_signal.diastolic_bp, 30, 160)

    return request


def parse_consent(data: dict) -> Consent:
    patient_id = str(data.get("patient_id", "")).strip()
    if not patient_id:
        raise ValidationError("patient_id is required")
    return Consent(
        patient_id=patient_id,
        data_processing=bool(data.get("data_processing")),
        ai_assistance=bool(data.get("ai_assistance")),
        emergency_override=bool(data.get("emergency_override")),
    )


def parse_preference(data: dict) -> Preference:
    user_id = str(data.get("user_id", "")).strip()
    if not user_id:
        raise ValidationError("user_id is required")
    widgets = [str(w).strip() for w in data.get("widgets", []) if str(w).strip()]
    return Preference(user_id=user_id, widgets=widgets, language=str(data.get("language", "en")).strip() or "en")
