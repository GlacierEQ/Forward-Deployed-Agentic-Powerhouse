---
name: ai-gateway
description: Multi-provider LLM routing (MiMo local > Groq > OpenRouter).
---
# Ai Gateway

## Architecture
Routes LLM requests through a cascading fallback chain:
1. **MiMo Local** (lowest latency, zero cost) — preferred when available on device.
2. **Groq** (fast inference, API key required via `GROQ_API_KEY`).
3. **OpenRouter** (broadest model selection, fallback via `OPENROUTER_API_KEY`).

## Routing Logic
- If `model_preference` is `auto`, try MiMo → Groq → OpenRouter.
- If a specific provider is requested, route directly.
- On timeout (>30s) or HTTP 5xx, cascade to the next provider.

## Integration
The gateway is consumed by `apex-connector-mesh` via the `llm.route` capability.
Credentials are loaded from `env-vars` / Supabase vault during bootup.
