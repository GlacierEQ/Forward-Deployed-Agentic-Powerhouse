---
name: apex-memory-substrate
description: Durable Intelligence Layer — Pointer-indexed persistence (Aspen-Grove), verified reasoning chains (Longest-Horizon), hybrid retrieval (Mem0, Supermemory, Pinecone, Qdrant, Context7), token compression, High Council multi-VP adjudication. Composes aspen-grove-core, longest-horizon, memory-unified, unified-memory-connect, token-optimizer.
version: 1.0.0
status: active
---

# APEX Memory Substrate — Mega-Skill 5

**Durable Intelligence Layer** — Persistent, compressed, adjudicated memory across sessions.

## Composed Sub-Skills

| Sub-Skill | Role | Entry Point |
|-----------|------|-------------|
| aspen-grove-core | Pointer-indexed persistence, quantum memory graph, SHA-256 integrity, auto-heal | `aspen-grove-core` skill |
| longest-horizon | Deep time memory, sequential reasoning, High Council adjudication | `longest-horizon` skill |
| memory-unified | Multi-layer semantic search (Mem0, Supermemory, Pinecone, Qdrant, Context7) | `memory-unified` skill |
| unified-memory-connect | Memory bridge | `unified-memory-connect` skill |
| token-optimizer | Context/token optimization via pointer compression | `token-optimizer` skill |

## Unified Capabilities (apex.capabilities/v1)

```yaml
schema: apex.capabilities/v1
repository: GlacierEQ/Pro-DOCTOR-STRANGE
mega_skill: apex-memory-substrate
capabilities:
  - id: memory.persist
    description: Pointer-indexed durable state with quantum references
    entrypoint: aspen-grove-core
    interface: library|http
    inputs:
      - key: {type: string, required: true}
      - value: {type: object}
      - ttl: {type: integer}
    outputs:
      - pointer: {type: string}
      - hash: {type: string}

  - id: memory.sequence
    description: Verified reasoning chains with sequential thinking
    entrypoint: longest-horizon
    interface: library|http
    inputs:
      - premise: {type: string, required: true}
      - steps: {type: array, items: {type: string}}
    outputs:
      - chain: {type: array}
      - verification: {type: object}

  - id: memory.search
    description: Hybrid retrieval (exact + sparse + dense + graph + temporal + authority)
    entrypoint: unified-memory_router
    interface: cli|library|http
    inputs:
      - query: {type: string, required: true}
      - layers: {type: array, items: {type: string}}
      - top_k: {type: integer, default: 4}
      - filters: {type: object}
    outputs:
      - results: {type: array}
    dependencies: [memory-unified, unified-memory-connect]

  - id: memory.compress
    description: Aspen-Grove pointer compression for token efficiency (~85% reduction)
    entrypoint: aspen-grove-core + token-optimizer
    interface: library|http
    inputs:
      - content: {type: string, required: true}
      - compression_level: {type: string, enum: [pointer, summary, hash], default: pointer}
    outputs:
      - compressed: {type: string}
      - original_tokens: {type: integer}
      - compressed_tokens: {type: integer}
      - reduction_pct: {type: number}

  - id: memory.adjudicate
    description: High Council multi-VP adjudication for conflicts
    entrypoint: longest-horizon
    interface: library|http
    inputs:
      - conflicting_items: {type: array, items: {type: object}}
      - criteria: {type: string}
    outputs:
      - verdict: {type: object}
      - reasoning: {type: array}
```

## CLI Interface

```bash
apex-memory <command> [options]

# Persist
apex-memory persist --key "case.1fdv.timeline" --value '{"events": [...]}' --ttl 86400

# Sequence
apex-memory sequence --premise "Void orders are attackable at any time" --steps step1.json

# Search
apex-memory search --query "HFCR 60(b)(4) void judgment" --layers mem0,supermemory,pinecone --top-k 10

# Compress
apex-memory compress --file brief.md --level pointer

# Adjudicate
apex-memory adjudicate --items conflicts.json --criteria "legal_authority_hierarchy"
```

## Verification Gates

| Gate | Test | Pass Criteria |
|------|------|---------------|
| G1 | `persist` + retrieve | Pointer resolves, hash matches, <5ms latency |
| G2 | `sequence` | Chain verified, each step logically follows |
| G3 | `search` | Results from ≥3 layers, relevance >0.7 |
| G4 | `compress` | ≥80% token reduction, lossless reconstruction |
| G5 | `adjudicate` | Verdict with reasoning, no unresolved conflicts |