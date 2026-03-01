from __future__ import annotations

from dataclasses import dataclass


@dataclass
class HealthSignal:
    heart_rate: int
    spo2: int
    systolic_bp: int
    diastolic_bp: int


@dataclass
class TriageRequest:
    patient_id: str
    symptoms: list[str]
    notes: str
    language: str
    health_signal: HealthSignal


def parse_triage_request(data: dict) -> TriageRequest:
    hs = data.get("health_signal", {})
    req = TriageRequest(
        patient_id=str(data.get("patient_id", "")),
        symptoms=[str(s) for s in data.get("symptoms", [])],
        notes=str(data.get("notes", "")),
        language=str(data.get("language", "en")),
        health_signal=HealthSignal(
            heart_rate=int(hs.get("heart_rate", 0)),
            spo2=int(hs.get("spo2", 0)),
            systolic_bp=int(hs.get("systolic_bp", 0)),
            diastolic_bp=int(hs.get("diastolic_bp", 0)),
        ),
    )

    if not (3 <= len(req.patient_id) <= 64):
        raise ValueError("patient_id out of range")
    if not req.symptoms:
        raise ValueError("symptoms required")
    if not (50 <= req.health_signal.spo2 <= 100):
        raise ValueError("spo2 out of range")
    return req
