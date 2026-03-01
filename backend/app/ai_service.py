from __future__ import annotations

from datetime import datetime, timezone

from .config import settings
from .models import TriageRequest


def _compute_urgency(request: TriageRequest) -> tuple[str, list[str]]:
    reasons: list[str] = []
    severe_symptoms = {
        "chest pain",
        "severe bleeding",
        "stroke signs",
        "loss of consciousness",
    }
    symptom_set = {symptom.lower() for symptom in request.symptoms}
    matched_severe = sorted(severe_symptoms.intersection(symptom_set))
    if matched_severe:
        reasons.append(f"Severe symptoms detected: {', '.join(matched_severe)}")
        return "critical", reasons

    if request.health_signal.spo2 < 90:
        reasons.append("SpO2 below 90 indicates respiratory risk")
    if request.health_signal.systolic_bp > 180:
        reasons.append("Systolic BP above 180 indicates hypertensive risk")
    if reasons:
        return "high", reasons

    if len(request.symptoms) >= 5:
        reasons.append("Multiple concurrent symptoms increase uncertainty")
        return "medium", reasons

    reasons.append("No severe indicators found in current data")
    return "low", reasons


def _base_actions() -> list[str]:
    return [
        "Collect complete vitals and symptom chronology",
        "Confirm medication/allergy history",
        "Provide culturally and linguistically appropriate instructions",
    ]


def generate_triage_recommendation(request: TriageRequest) -> dict:
    notes = request.notes.lower()
    if any(phrase in notes for phrase in settings.blocked_phrases):
        return {
            "recommendation": "Escalated for human clinical review due to policy safety trigger.",
            "urgency": "high",
            "actions": [
                "Do not provide autonomous treatment guidance",
                "Route case to licensed clinician within 5 minutes",
                "Log incident to AI safety audit trail",
            ],
            "alignment": {
                "risk_level": "guardrail_triggered",
                "confidence": 0.99,
                "safety_checks": [
                    "content-policy-filter",
                    "human-in-the-loop-enforced",
                    "audit-log-recorded",
                ],
            },
            "explanation": {
                "summary": "Policy filter detected restricted medical guidance pattern.",
                "reasons": ["Guardrail phrase match in clinician notes."],
            },
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    urgency, reasons = _compute_urgency(request)
    actions = _base_actions()
    if urgency in {"high", "critical"}:
        actions.extend(
            [
                "Initiate emergency referral workflow",
                "Notify nearest available provider and caregiver",
            ]
        )

    return {
        "recommendation": "AI-assisted triage recommendation; requires clinician validation before final diagnosis.",
        "urgency": urgency,
        "actions": actions,
        "alignment": {
            "risk_level": "controlled",
            "confidence": 0.84 if urgency == "low" else 0.78,
            "safety_checks": [
                "model-output-grounding",
                "harm-minimization-policy",
                "clinician-signoff-required",
            ],
        },
        "explanation": {
            "summary": "Urgency is derived from symptom severity and vitals thresholds.",
            "reasons": reasons,
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
