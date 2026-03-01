import json
import unittest

from app.main import handle_request


class ApiTests(unittest.TestCase):
    def test_health(self) -> None:
        status, payload = handle_request("GET", "/health", {}, b"")
        data = json.loads(payload)
        self.assertEqual(status, 200)
        self.assertEqual(data["status"], "ok")

    def test_login_and_triage(self) -> None:
        status, payload = handle_request(
            "POST",
            "/auth/token",
            {},
            json.dumps({"username": "clinician", "password": "SecurePass123!"}).encode(),
        )
        self.assertEqual(status, 200)
        token = json.loads(payload)["access_token"]

        triage_payload = {
            "patient_id": "P-001",
            "symptoms": ["headache", "fatigue"],
            "notes": "No red flags",
            "language": "en",
            "health_signal": {"heart_rate": 89, "spo2": 97, "systolic_bp": 122, "diastolic_bp": 79},
        }
        status, payload = handle_request(
            "POST",
            "/api/triage",
            {"authorization": f"Bearer {token}"},
            json.dumps(triage_payload).encode(),
        )
        self.assertEqual(status, 200)
        self.assertIn("clinician-signoff-required", json.loads(payload)["alignment"]["safety_checks"])

    def test_guardrail_trigger(self) -> None:
        _, payload = handle_request(
            "POST",
            "/auth/token",
            {},
            json.dumps({"username": "clinician", "password": "SecurePass123!"}).encode(),
        )
        token = json.loads(payload)["access_token"]

        triage_payload = {
            "patient_id": "P-002",
            "symptoms": ["dizziness"],
            "notes": "Need illegal drug dosage now",
            "language": "en",
            "health_signal": {"heart_rate": 77, "spo2": 96, "systolic_bp": 118, "diastolic_bp": 72},
        }
        status, payload = handle_request(
            "POST",
            "/api/triage",
            {"authorization": f"Bearer {token}"},
            json.dumps(triage_payload).encode(),
        )
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(payload)["alignment"]["risk_level"], "guardrail_triggered")


if __name__ == "__main__":
    unittest.main()
