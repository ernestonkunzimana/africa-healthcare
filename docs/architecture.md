# Architecture Overview

## 1. End-to-End System Blueprint

The platform is designed as a secure-by-design healthcare mesh:

- **frontend/**: dynamic web command center with configurable widgets, offline queueing, and explainable result views.
- **backend/**: Python API service for auth, consent, privacy policy, preferences, triage, and AI safety guardrails.
- **infra/**: Docker + Kubernetes deployment assets for local and cloud/on-prem runtime.
- **docs/**: living technical and governance documentation.

## 2. Reliability and Safe-Fail Design

- Frontend offline queue preserves triage intent when internet is down.
- Automatic sync resumes when connectivity returns.
- Backend enforces explicit fail-closed policies for missing auth, consent, or data residency mismatch.

## 3. Sovereignty, Privacy, and Compliance Design

- Deployment-country and allowlist-country controls are environment-driven.
- Policy endpoint exposes privacy and residency controls transparently.
- Local-first storage pattern avoids dependency on external cloud vendors.

## 4. Explainability and User-Centric UX

- Triage results include an explanation summary and concrete reasons.
- Clinicians select preferred dashboard widgets (dynamic UI, not one-size-fits-all).
- Human-in-the-loop remains mandatory for diagnosis.
