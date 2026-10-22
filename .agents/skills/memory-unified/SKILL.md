---
name: memory-unified
description: Multi-layer semantic search across Mem0, Supermemory, Pinecone, Qdrant, Context7.
---
# Memory Unified

## Search Pipeline
1. Parse the query into embedding vector + keyword terms.
2. Fan out to all configured memory layers in parallel.
3. Collect results with source attribution.
4. Deduplicate by content hash.
5. Rank by composite score (vector similarity + recency + authority).
6. Return top-k results with provenance.

## Configuration
Each layer can be enabled/disabled independently. Credentials are loaded via `auth` + `env-vars`.
