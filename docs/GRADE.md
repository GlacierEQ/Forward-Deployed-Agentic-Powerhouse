# Verification status — v0.7.1

This document records objective verification surfaces. It does not self-grade the project.

| Surface | Current contract |
|---|---|
| Stage spine | DISCOVER → FRAME → BUILD → INTEGRATE → EVALUATE → PROVE → DEPLOY |
| Invert scan | Pattern + semantic checks with confidence/negation handling |
| Agent scaffold | Orchestrator / policy / memory / tools loop |
| CI matrix | Python 3.11–3.13 |
| Coverage gate | 70% minimum |
| Optional private integration | VERIFIED only when the pinned checkout succeeds and validate-only invocation actually runs |
| Missing private integration | UNVERIFIED, never promoted to VERIFIED |
| External authority | Human-gated; approval_packet_only |

## Evidence interpretation

A green core CI run proves the self-contained public proof path passed its configured checks. It does **not** prove an optional private integration ran.

Catalog snapshots are inventory evidence, not live runtime verification. Live integration claims require an executed validation receipt from the relevant integration path.

The project should be evaluated from reproducible behavior, tests, receipts, and explicit evidence state rather than an author-assigned score.
