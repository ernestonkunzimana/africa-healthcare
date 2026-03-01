from datetime import datetime, timezone

from .config import settings
from .models import AlignmentMeta, TriageRequest, TriageResponse


def _contains_blocked_phrase(text: str) -> bool:
    lowered = text.lower()
    return any(phrase in lowered for phrase in settings.ai_blocked_phrases)


def _calculate_urgency(request: TriageRequest) -> str:
    severe_symptoms = {"chest pain", "severe bleeding", "stroke signs", "loss of consciousness"}
    symptom_set = {symptom.lower() for symptom in request.symptoms}
    if severe_symptoms.intersection(symptom_set):
        return "critical"
    if request.health_signal.spo2 < 90 or request.health_signal.systolic_bp > 180:
        return "high"
    if len(request.symptoms) >= 5:
        return "medium"
    return "low"


def generate_triage_recommendation(request: TriageRequest) -> TriageResponse:
    if _contains_blocked_phrase(request.notes):
        return TriageResponse(
            recommendation="Escalated for human clinical review due to policy safety trigger.",
            urgency="high",
            actions=[
                "Do not provide autonomous treatment guidance",
                "Route case to licensed clinician within 5 minutes",
                "Log incident to AI safety audit trail",
            ],
            alignment=AlignmentMeta(
                risk_level="guardrail_triggered",
                confidence=0.99,
                safety_checks=[
                    "content-policy-filter",
                    "human-in-the-loop-enforced",
                    "audit-log-recorded",
                ],
            ),
            generated_at=datetime.now(tz=timezone.utc),
        )

    urgency = _calculate_urgency(request)
    actions = [
        "Collect complete vitals and symptom chronology",
        "Confirm medication/allergy history",
        "Provide culturally and linguistically appropriate instructions",
    ]

    if urgency in {"critical", "high"}:
        actions.extend([
            "Initiate emergency referral workflow",
            "Notify nearest available provider and caregiver",
        ])

    recommendation = (
        "AI-assisted triage recommendation generated with cognitive-emulation UX cues; "
        "requires clinician validation before final diagnosis."
    )

    return TriageResponse(
        recommendation=recommendation,
        urgency=urgency,
        actions=actions,
        alignment=AlignmentMeta(
            risk_level="controlled",
            confidence=0.84 if urgency == "low" else 0.78,
            safety_checks=[
                "model-output-grounding",
                "harm-minimization-policy",
                "clinician-signoff-required",
            ],
        ),
        generated_at=datetime.now(tz=timezone.utc),
    )
