# Security Model

## Threat Model Focus

- Credential theft and token replay.
- Prompt injection and unsafe medical guidance generation.
- API misuse and PII overexposure.
- Cross-border exfiltration and sovereignty violations.

## Implemented Controls

- Signed JWT tokens with expiry and claim checks.
- Input validation constraints and explicit error boundaries.
- AI blocked-phrase policy and escalation mode.
- Consent gate before triage processing.
- Country-based data residency allowlist.
- Local-first persistence designed for sovereign in-country hosting.

## Sovereignty & Privacy Principles

- Default policy disallows cross-border transfer.
- Deployers define in-country storage via `AH_STORAGE_DIR` and country policy via `AH_ALLOWED_DATA_COUNTRIES`.
- Platform policy explicitly forbids external third-party data sharing.

## Required Production Hardening

- Use managed IAM with MFA and device trust.
- Encrypt data at rest with customer-managed keys held in-country.
- Add tamper-evident audit trail with legal evidence retention.
- Enforce legal consent registry and data-subject rights workflows.
