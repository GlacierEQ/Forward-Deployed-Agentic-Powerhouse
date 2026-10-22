---
name: auth
description: Authentication/authorization with least-privilege credential scoping.
---
# Auth

## Protocol
1. Determine the minimum required scope for the requested operation (read/write/admin).
2. Load credentials from the vault hierarchy: env vars → `.operator_key_vault` → Supabase vault.
3. Issue a scoped token with an expiry (default: 1 hour).
4. Never expose credentials in logs or agent output.

## Supported Credential Sources
- Environment variables (`GITHUB_PAT`, `GEMINI_API_KEY`, etc.)
- File vaults (`gatekeeper.env`, `credentials.env`)
- Supabase PostgreSQL vault (457+ indexed keys)
- OAuth tokens (Antigravity OAuth)
