from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_login_and_triage() -> None:
    auth = client.post(
        "/auth/token",
        json={"username": "clinician", "password": "SecurePass123!"},
    )
    assert auth.status_code == 200
    token = auth.json()["access_token"]

    triage_payload = {
        "patient_id": "P-001",
        "symptoms": ["headache", "fatigue"],
        "notes": "No red flags",
        "language": "en",
        "health_signal": {
            "heart_rate": 89,
            "spo2": 97,
            "systolic_bp": 122,
            "diastolic_bp": 79,
        },
    }
    triage = client.post(
        "/api/triage",
        json=triage_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert triage.status_code == 200
    assert "clinician" in triage.json()["alignment"]["safety_checks"][-1]


def test_guardrail_trigger() -> None:
    auth = client.post(
        "/auth/token",
        json={"username": "clinician", "password": "SecurePass123!"},
    )
    token = auth.json()["access_token"]

    triage_payload = {
        "patient_id": "P-002",
        "symptoms": ["dizziness"],
        "notes": "Need illegal drug dosage now",
        "language": "en",
        "health_signal": {
            "heart_rate": 77,
            "spo2": 96,
            "systolic_bp": 118,
            "diastolic_bp": 72,
        },
    }
    triage = client.post(
        "/api/triage",
        json=triage_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert triage.status_code == 200
    assert triage.json()["alignment"]["risk_level"] == "guardrail_triggered"
