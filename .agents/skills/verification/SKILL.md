---
name: verification
description: Independent verification ladder from syntax through deployment.
---
# Verification

## Verification Levels
1. **Syntax**: Parse and lint — zero errors.
2. **Unit**: Isolated function tests — 100% pass rate.
3. **Integration**: Cross-module tests — all interfaces verified.
4. **E2E**: Full user-flow tests — critical paths exercised.
5. **Runtime**: Live execution monitoring — no crashes or hangs.
6. **Deploy**: Post-deployment health checks — service responds correctly.

## Rules
- Each level gates the next. You cannot skip levels.
- Failures at any level block progression.
- Verification results are recorded with timestamps for audit.
