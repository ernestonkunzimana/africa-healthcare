# API Contracts

## Auth

### POST /auth/token
Request:
```json
{ "username": "clinician", "password": "SecurePass123!" }
```
Response:
```json
{ "access_token": "<jwt>", "token_type": "bearer" }
```

## Triage

### POST /api/triage
Headers:
- `Authorization: Bearer <jwt>`

Request:
```json
{
  "patient_id": "P-001",
  "symptoms": ["headache", "fatigue"],
  "notes": "free text context",
  "language": "en",
  "health_signal": {
    "heart_rate": 90,
    "spo2": 97,
    "systolic_bp": 120,
    "diastolic_bp": 80
  }
}
```

Response:
```json
{
  "recommendation": "...",
  "urgency": "low|medium|high|critical",
  "actions": ["..."],
  "alignment": {
    "risk_level": "controlled|guardrail_triggered",
    "confidence": 0.84,
    "safety_checks": ["..."]
  },
  "generated_at": "2026-01-01T00:00:00Z"
}
```
