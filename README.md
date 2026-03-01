# Africa Healthcare Nexus

End-to-end secure-by-design healthcare platform foundation with AI-aligned triage workflows, dynamic clinician UX, and cloud/on-prem deployment assets.

## What is new in this revision

- **Fail-safe operation**: frontend supports online/offline mode with a local request queue that safely syncs when internet returns.
- **Dynamic UX**: clinicians can choose dashboard widgets and save preferences.
- **Data sovereignty**: triage processing is blocked unless request country is in the allowlist (`AH_ALLOWED_DATA_COUNTRIES`).
- **Consent-first workflow**: triage requires explicit patient consent (`/api/consent`).
- **Explainability**: triage responses include explanation summary + reasons.

## Repository Structure

- `frontend/` — Dynamic web app command center.
- `backend/` — Python API service with auth, consent, privacy, triage, and guardrails.
- `infra/` — Docker Compose and Kubernetes manifests.
- `docs/` — architecture, API contracts, security model, AI safety, and roadmap.

## Quick Start (Local)

### 1) Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

### 2) Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend default API target is `http://localhost:8000` and can be overridden with `window.AH_API_BASE`.

## Key Environment Variables

- `AH_DEPLOYMENT_COUNTRY` (default: `Rwanda`)
- `AH_ALLOWED_DATA_COUNTRIES` (default: `Rwanda`)
- `AH_STORAGE_DIR` (default: `./backend_data`)
- `AH_JWT_SECRET`

## Validation Commands

```bash
python -m compileall backend/app
cd backend && python -m unittest discover -s tests -p 'test_*.py'
cd frontend && npm install && npm run build
```

## Core Guarantees

- Offline-capable, fail-safe request queuing.
- Consent-based processing.
- In-country data control policies.
- Explainable AI-assisted triage.
- Human-in-the-loop and safety guardrails.
