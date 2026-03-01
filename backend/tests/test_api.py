import json
import shutil
import tempfile
import unittest
from pathlib import Path

from app import config
from app.main import handle_request


class ApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp(prefix="ah-test-")
        config.settings = config.Settings(
            app_name="Africa Healthcare Platform",
            api_version="v1",
            access_token_expire_minutes=30,
            jwt_secret="test-secret",
            blocked_phrases=("illegal drug dosage",),
            deployment_country="Rwanda",
            allowed_data_countries=("Rwanda", "Kenya"),
            storage_dir=self.tmp,
        )
        # clear persisted files from lazy store paths
        for fn in ["consents.json", "preferences.json", "audit.json"]:
            p = Path(self.tmp) / fn
            if p.exists():
                p.unlink()

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _token(self) -> str:
        status, payload = handle_request(
            "POST",
            "/auth/token",
            {},
            json.dumps({"username": "clinician", "password": "SecurePass123!"}).encode(),
        )
        self.assertEqual(status, 200)
        return json.loads(payload)["access_token"]

    def test_health(self) -> None:
        status, payload = handle_request("GET", "/health", {}, b"")
        data = json.loads(payload)
        self.assertEqual(status, 200)
        self.assertEqual(data["deployment_country"], "Rwanda")

    def test_privacy_policy(self) -> None:
        status, payload = handle_request("GET", "/api/privacy/policy", {}, b"")
        self.assertEqual(status, 200)
        data = json.loads(payload)
        self.assertEqual(data["data_residency"]["cross_border_transfer"], "disabled")

    def test_consent_required(self) -> None:
        token = self._token()
        triage_payload = {
            "patient_id": "P-001",
            "symptoms": ["headache"],
            "notes": "No red flags",
            "language": "en",
            "country": "Rwanda",
            "health_signal": {"heart_rate": 89, "spo2": 97, "systolic_bp": 122, "diastolic_bp": 79},
        }
        status, _ = handle_request(
            "POST",
            "/api/triage",
            {"authorization": f"Bearer {token}"},
            json.dumps(triage_payload).encode(),
        )
        self.assertEqual(status, 403)

    def test_consent_then_triage_explainable(self) -> None:
        token = self._token()
        handle_request(
            "POST",
            "/api/consent",
            {},
            json.dumps(
                {
                    "patient_id": "P-001",
                    "data_processing": True,
                    "ai_assistance": True,
                    "emergency_override": False,
                }
            ).encode(),
        )

        triage_payload = {
            "patient_id": "P-001",
            "symptoms": ["headache", "fatigue"],
            "notes": "No red flags",
            "language": "en",
            "country": "Rwanda",
            "health_signal": {"heart_rate": 89, "spo2": 97, "systolic_bp": 122, "diastolic_bp": 79},
        }
        status, payload = handle_request(
            "POST",
            "/api/triage",
            {"authorization": f"Bearer {token}"},
            json.dumps(triage_payload).encode(),
        )
        self.assertEqual(status, 200)
        data = json.loads(payload)
        self.assertIn("explanation", data)
        self.assertTrue(data["explanation"]["reasons"])

    def test_data_residency_block(self) -> None:
        token = self._token()
        handle_request(
            "POST",
            "/api/consent",
            {},
            json.dumps(
                {
                    "patient_id": "P-900",
                    "data_processing": True,
                    "ai_assistance": True,
                    "emergency_override": False,
                }
            ).encode(),
        )
        triage_payload = {
            "patient_id": "P-900",
            "symptoms": ["headache"],
            "notes": "No red flags",
            "language": "en",
            "country": "USA",
            "health_signal": {"heart_rate": 80, "spo2": 97, "systolic_bp": 120, "diastolic_bp": 70},
        }
        status, _ = handle_request(
            "POST",
            "/api/triage",
            {"authorization": f"Bearer {token}"},
            json.dumps(triage_payload).encode(),
        )
        self.assertEqual(status, 403)

    def test_preferences_roundtrip(self) -> None:
        status, _ = handle_request(
            "POST",
            "/api/preferences",
            {},
            json.dumps({"user_id": "clinician", "widgets": ["consent", "triage"], "language": "en"}).encode(),
        )
        self.assertEqual(status, 200)

        status, payload = handle_request("GET", "/api/preferences/clinician", {}, b"")
        self.assertEqual(status, 200)
        data = json.loads(payload)
        self.assertIn("consent", data["preferences"]["widgets"])


if __name__ == "__main__":
    unittest.main()
