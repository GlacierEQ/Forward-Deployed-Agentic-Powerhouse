---
name: env-vars
description: Environment variable and secret management.
---
# Env Vars

## Loading Order (highest priority first)
1. Process environment (`os.environ`)
2. `.operator_key_vault/gatekeeper.env`
3. `.apex_vault/credentials.env`
4. Supabase PostgreSQL vault
5. `.env` files in project root

## Security Rules
- Never log secret values.
- Never include secrets in agent output or artifacts.
- Prefer vault reads over hardcoded values.
- Rotate expired tokens automatically when possible.
