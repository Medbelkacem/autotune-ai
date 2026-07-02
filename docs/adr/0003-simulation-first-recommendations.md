# ADR 0003 — Simulation-first, tuner-signed recommendations

Date: 2026-02-05  ·  Status: Accepted

## Context
The blast radius of an ECU write is a damaged engine, void warranty, or emissions violation. Regulators (UNECE R155/R156, EPA, KBA) require cryptographic provenance of any calibration change.

## Decision
- Every recommendation is generated in `status='simulation'` and scored against a 1D engine model *before* it ever surfaces to a human.
- Approval requires an ed25519 signature over the canonical JSON of the bundle, signed by a credentialed `tuner` using a hardware-backed key (YubiKey or Secure Enclave).
- The system will REFUSE, at policy layer, defeat-device modifications and low-safety-score bundles.

## Consequences
- Legal + regulatory exposure is bounded.
- User friction: tuners must onboard a hardware key. Mitigated with webauthn/passkey UX.
- We can produce a full audit chain (report → recommendation → signature → flash log) for OEM/reg audits.
