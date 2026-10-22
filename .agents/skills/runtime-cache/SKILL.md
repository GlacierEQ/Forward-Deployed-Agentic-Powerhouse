---
name: runtime-cache
description: Multi-layer caching for sub-second tool execution.
---
# Runtime Cache

## Cache Layers
1. **L1 — In-Memory**: Python dict, ~0ms latency, lost on process restart.
2. **L2 — File-Based**: JSON files in `.apex_cache/`, survives restarts.
3. **L3 — Remote**: Redis/Supabase for cross-session persistence.

## Cache Policy
- Tool schema definitions: cached at L1 (immutable per session).
- Connector discovery results: cached at L2 with 5-minute TTL.
- Memory search results: cached at L2 with 1-minute TTL.
- Never cache: credentials, mutable state, write operations.
