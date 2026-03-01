# Security Model

## Threat Model Focus

- Credential theft and token replay.
- Prompt injection and unsafe medical guidance generation.
- API misuse and PII overexposure.
- Supply-chain compromise in CI/CD.

## Implemented Controls

- BCrypt password hashing in backend auth store.
- Signed JWT tokens with expiry.
- CORS restrictions for known origins.
- Input validation constraints via Pydantic types.
- AI blocked-phrase policy and escalation mode.
- Clinician-signoff requirement in recommendation pathway.

## Required Production Hardening

- Move auth to managed IdP (OIDC/SAML + MFA).
- Rotate secrets via vault/KMS; remove static defaults.
- Add mTLS service-to-service auth.
- Add WAF, rate limits, anomaly detection.
- Add immutable audit trail (blockchain anchor if required by jurisdiction).
