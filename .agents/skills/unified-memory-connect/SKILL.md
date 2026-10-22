---
name: unified-memory-connect
description: Bridge connector for unified memory substrate.
---
# Unified Memory Connect

## Role
Thin adapter layer that normalizes the interface between:
- `memory-unified` (search/retrieval)
- `memory-connect` (transport)
- `aspen-grove-core` (pointer persistence)

## Protocol
Exposes a single `query()` interface that fans out across all memory layers and returns unified, deduplicated results with provenance metadata.
