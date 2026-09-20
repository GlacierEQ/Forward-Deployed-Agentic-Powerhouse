---
name: apex-connector-mesh
description: Universal Integration Fabric — 32+ MCP servers (GitHub, Google, Notion, Dropbox, Exa, Tavily, Jina, legal), multi-provider LLM routing (MiMo > Groq > OpenRouter), unified memory query (Mem0, Supermemory, Pinecone, Qdrant, Context7), Supabase vault access. Composes smithery-holographic-mesh, ai-gateway, ai-sdk, chat-sdk, vercel-*, memory-unified, unified-memory-connect, memory-connect, supabase_vault_client.
version: 1.0.0
status: active
---

# APEX Connector Mesh — Mega-Skill 2

**Universal Integration Fabric** — Single interface to all external capabilities.

## Composed Sub-Skills

| Sub-Skill | Role | Entry Point |
|-----------|------|-------------|
| smithery-holographic-mesh | 32+ MCP servers (GitHub, Google, Notion, Dropbox, Exa, Tavily, Jina, legal) | `scripts/connector_hub_supreme.py` |
| ai-gateway | Multi-provider LLM routing (MiMo local > Groq > OpenRouter) | `ai-gateway` skill |
| ai-sdk | Vercel AI SDK integration | `ai-sdk` skill |
| chat-sdk | Chat interface SDK | `chat-sdk` skill |
| vercel-functions/storage/sandbox/firewall/platform-ops/agent | Vercel ecosystem | `vercel-*` skills |
| memory-unified | Multi-layer memory (Mem0, Supermemory, Pinecone, Qdrant, Context7) | `memory-unified` skill |
| unified-memory-connect | Memory bridge | `unified-memory-connect` skill |
| memory-connect | Memory bridge | `memory-connect` skill |
| supabase_vault_client | PostgreSQL vault | `scripts/supabase_vault_client.py` |

## Unified Capabilities (apex.capabilities/v1)

```yaml
schema: apex.capabilities/v1
repository: GlacierEQ/Pro-DOCTOR-STRANGE
mega_skill: apex-connector-mesh
capabilities:
  - id: connector.discover
    description: Discover all available MCP servers, APIs, services
    entrypoint: scripts/connector_hub_supreme.py status
    interface: cli|library|http
    outputs:
      - active_services: integer
      - total_mcp_servers: integer
      - server_categories: array
      - services: object
    confidence: verified

  - id: connector.invoke
    description: Invoke any connector with retry, caching, normalization
    entrypoint: connector_hub_supreme.py invoke
    interface: library|http
    inputs:
      - service: {type: string, required: true}
      - method: {type: string, required: true}
      - params: {type: object}
    outputs:
      - result: object
      - receipt: object
    dependencies: [smithery-holographic-mesh]

  - id: connector.search
    description: Unified search across GitHub, Google, Notion, Dropbox, Exa, Tavily, Jina, legal, memory
    entrypoint: connector_hub_supreme.py search
    interface: cli|library|http
    inputs:
      - query: {type: string, required: true}
      - sources: {type: array, items: {type: string}}
      - top_k: {type: integer, default: 10}
    outputs:
      - results: array
    dependencies: [smithery-holographic-mesh]

  - id: llm.route
    description: Route to best LLM (MiMo local > Groq > OpenRouter) with fallback
    entrypoint: ai-gateway
    interface: library|http
    inputs:
      - prompt: {type: string, required: true}
      - model_preference: {type: string, enum: [auto, mimo, groq, openrouter], default: auto}
      - max_tokens: {type: integer, default: 65536}
    outputs:
      - response: string
      - model_used: string
      - tokens: integer
    dependencies: [ai-gateway, ai-sdk]

  - id: memory.query
    description: Semantic search across Mem0, Supermemory, Pinecone, Qdrant, Context7
    entrypoint: unified-memory_router
    interface: cli|library|http
    inputs:
      - query: {type: string, required: true}
      - layers: {type: array, items: {type: string}}
      - top_k: {type: integer, default: 4}
    outputs:
      - results: array
    dependencies: [memory-unified, unified-memory-connect, memory-connect]

  - id: vault.read
    description: Read secrets from Supabase PostgreSQL vault
    entrypoint: supabase_vault_client
    interface: library|http
    inputs:
      - key: {type: string, required: true}
    outputs:
      - value: string
    dependencies: [supabase_vault_client]

  - id: github.operate
    description: GitHub operations via MCP (repos, issues, PRs, actions, codespaces)
    entrypoint: smithery-holographic-mesh github
    interface: library|http
    inputs:
      - operation: {type: string, required: true}
      - params: {type: object}
    outputs:
      - result: object
    dependencies: [smithery-holographic-mesh]

  - id: google.operate
    description: Google Workspace operations via MCP (Drive, Docs, Sheets, Gmail, Photos)
    entrypoint: smithery-holographic-mesh google
    interface: library|http
    inputs:
      - service: {type: string, required: true}
      - operation: {type: string, required: true}
      - params: {type: object}
    outputs:
      - result: object
    dependencies: [smithery-holographic-mesh]
```

## CLI Interface

```bash
apex-connector <command> [options]

# Connector management
apex-connector discover                    # List all active services
apex-connector search --query "..."       # Unified search across all sources
apex-connector invoke --service github --method list_repos --params '{}'

# LLM routing
apex-connector llm --prompt "..." --model auto

# Memory query
apex-connector memory --query "..." --layers mem0,supermemory,pinecone,qdrant,context7

# Vault
apex-connector vault --key GITHUB_PAT

# Direct service operations
apex-connector github --op list_repos --params '{"org": "GlacierEQ"}'
apex-connector google --service drive --op list_files --params '{}'
```

## Verification Gates

| Gate | Test | Pass Criteria |
|------|------|---------------|
| G1 | `discover` | 12/12 services ONLINE, 32 MCP servers |
| G2 | `search` | Returns results from ≥3 source categories |
| G3 | `llm.route` | Response from MiMo (primary) or fallback |
| G4 | `memory.query` | Results from ≥2 memory layers |
| G5 | `vault.read` | Returns secret value for valid key |
| G6 | `github.operate` | Successful API call to GitHub |
| G7 | `google.operate` | Successful API call to Google Workspace |