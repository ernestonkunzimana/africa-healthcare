# Africa Healthcare Nexus

End-to-end secure-by-design healthcare platform foundation with AI-aligned triage workflows, futuristic clinician UX, and cloud-ready deployment assets.

## Repository Structure

- `frontend/` — React web app command center for clinician workflows.
- `backend/` — FastAPI API with authentication, triage, and AI safety guardrails.
- `infra/` — Docker Compose and Kubernetes manifests.
- `docs/` — architecture, API contracts, security model, AI safety, and roadmap.

## Quick Start (Local)

### 1) Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2) Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend default API target is `http://localhost:8000`.

## Full Stack via Docker

```bash
cd infra
docker compose up --build
```

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`

## Core Security and AI Safety Guarantees

- JWT-protected API endpoints.
- Guardrail-triggered human escalation mode.
- Explicit clinician-signoff requirement in AI output semantics.
- Strong input validation and controlled CORS policy.

## Documentation

- [Architecture](docs/architecture.md)
- [API Contracts](docs/api-contracts.md)
- [Security Model](docs/security-model.md)
- [AI Alignment & Safety](docs/ai-alignment-safety.md)
- [Roadmap MVP → V1](docs/roadmap-mvp-v1.md)
