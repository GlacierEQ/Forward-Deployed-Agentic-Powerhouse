---
name: release
description: Automated release with verification gates.
---
# Release

## Release Pipeline
1. **Gate: Syntax** — Zero lint/type errors.
2. **Gate: Tests** — All unit + integration tests pass.
3. **Gate: Benchmark** — No performance regression beyond threshold.
4. **Gate: Security** — No known vulnerabilities in dependencies.
5. **Build** — Production build succeeds.
6. **Tag** — Git tag with semantic version.
7. **Changelog** — Auto-generated from commit history.
8. **Deploy** — Push to target environment.

## Rollback
If any post-deploy health check fails, automatically revert to the previous version.
