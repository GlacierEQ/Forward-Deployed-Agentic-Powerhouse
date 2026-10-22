---
name: supermemory
description: "Supermemory living knowledge graph: persistent user profiles, semantic memory search, and RAG across conversations."
---

# Supermemory AI: Universal Memory & Knowledge Infrastructure

Supermemory is the persistent memory, user profile, and context management infrastructure for the APEX Holographic Mesh, powered by [Supermemory.ai](https://supermemory.ai).

## Core Capabilities

1. **Memory API (Learned User Context)**:
   - Dynamic extraction of facts and insights from conversation turns.
   - Automatically scopes to `containerTag: "glaciereq-apex"`.
   - Maintains evolving relationships between memories (updates, extends, derives).

2. **User Profiles**:
   - `get_profile`: Combines permanent static facts (Operator Casey Barton, GlacierEQ estate, legal posture) with episodic context from recent sessions.

3. **Semantic Search & RAG**:
   - `search_memory`: Natural-language semantic search across stored documents, notes, transcripts, and exhibits.
   - Multi-modal knowledge graph linking cases, pleadings, and code.

## Available MCP Tools (via `supermemory`)

- `search_memory`: Semantic search in active space (`query`, `containerTag`).
- `get_profile`: Read current user profile and context (`containerTag`).
- `add_memory` / `save-memory`: Store high-value learnings or decisions.
- `list_memories`: List recent extracted memory entries.
- `list_documents` / `get_document`: Inspect indexed documents and extracts.
- `list_spaces` / `who_am_i`: Inspect account spaces and permissions.
- `memory-graph`: Interactive visual graph of memories and document clusters.

## Python Integration Example

```python
import os, json, urllib.request

api_key = os.environ.get("SUPERMEMORY_API_KEY")

# Add memory via MCP bridge or API
payload = {
    "content": "Case 1FDV-23-0001009: HFCR 60(b)(4) void order challenge active under Stafford v. Dickison.",
    "containerTag": "glaciereq-apex",
    "metadata": {"domain": "legal", "priority": "P0"}
}
```

## Diagnostics CLI

```bash
# Check Supermemory MCP status
agy mcp list

# Test who_am_i via stdio bridge
python3 -c "
import subprocess, json
p = subprocess.run(['/root/bin/supermemory_mcp_server.py'], input=json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call', 'params': {'name': 'who_am_i', 'arguments': {}}}) + '\n', text=True, capture_output=True)
print(p.stdout)
"
```
