---
name: benchmark-suite
description: Performance benchmarking with before/after measurements.
---
# Benchmark Suite

## Metrics Collected
- **Throughput**: Operations per second.
- **Latency**: p50, p95, p99 response times.
- **Memory**: Peak RSS, heap allocation.
- **Token Cost**: Input/output token counts per operation.

## Usage
1. Establish a baseline measurement before changes.
2. Apply the change.
3. Re-measure and compute the delta.
4. Report pass/fail against defined thresholds.

## Integration
Consumed by `apex-engineering-excellence` via the `code.benchmark` capability.
