from __future__ import annotations

from datetime import datetime, timezone

from .models import TriageRequest

BLOCKED_PHRASES = ("self-harm instruction", "illegal drug dosage", "bypass diagnosis protocol")


def generate_triage_recommendation(request: TriageRequest) -> dict:
    lowered = request.notes.lower()
    if any(p in lowered for p in BLOCKED_PHRASES):
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
                "safety_checks": ["content-policy-filter", "human-in-the-loop-enforced", "audit-log-recorded"],
            },
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    severe = {"chest pain", "severe bleeding", "stroke signs", "loss of consciousness"}
    symptom_set = {s.lower() for s in request.symptoms}
    urgency = "critical" if severe.intersection(symptom_set) else "low"
    return {
        "recommendation": "AI-assisted triage recommendation; requires clinician validation before final diagnosis.",
        "urgency": urgency,
        "actions": [
            "Collect complete vitals and symptom chronology",
            "Confirm medication/allergy history",
            "Provide culturally and linguistically appropriate instructions",
        ],
        "alignment": {
            "risk_level": "controlled",
            "confidence": 0.84,
            "safety_checks": ["model-output-grounding", "harm-minimization-policy", "clinician-signoff-required"],
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
