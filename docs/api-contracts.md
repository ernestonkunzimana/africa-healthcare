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

## Privacy & Sovereignty

### GET /api/privacy/policy
Returns residency and sharing controls.

### POST /api/consent
Request:
```json
{
  "patient_id": "P-001",
  "data_processing": true,
  "ai_assistance": true,
  "emergency_override": false
}
```

### POST /api/preferences
Request:
```json
{ "user_id": "clinician", "widgets": ["consent", "triage"], "language": "en" }
```

### GET /api/preferences/{user_id}
Returns saved UI preferences.

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
  "country": "Rwanda",
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
  "explanation": {
    "summary": "...",
    "reasons": ["..."]
  },
  "generated_at": "2026-01-01T00:00:00Z"
}
```
