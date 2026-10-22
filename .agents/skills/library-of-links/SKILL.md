---
name: library-of-links
description: Curated Knowledge & Hard Science Registry with provenance tracking, domain categorization, and liveness verification.
---

# Library Of Links — Knowledge & Science Federation

Curated repository of external authorities, research databases, physics models, biology repositories, low-level engineering documentation, and legal forensics anchors.

## 📂 Registry Architecture
- **Storage:** JSON databases under [`data/`](file:///root/.agents/skills/library-of-links/data/)
  - [`physics.json`](file:///root/.agents/skills/library-of-links/data/physics.json) — Orbital mechanics, rocket propulsion, thermodynamics, NIST constants.
  - [`biology.json`](file:///root/.agents/skills/library-of-links/data/biology.json) — Genomics (NCBI), AlphaFold protein structures, UniProt.
  - [`engineering_dev.json`](file:///root/.agents/skills/library-of-links/data/engineering_dev.json) — Linux kernel architecture, SQLite WAL internals, PRoot/POSIX virtualization.
  - [`legal_forensics.json`](file:///root/.agents/skills/library-of-links/data/legal_forensics.json) — JEFS court portals, Cornell LII US Code/FRCP.
- **Monolith Bridge:** [`status/KNOWLEDGE_FEDERATION.md`](file:///data/data/com.termux/files/home/monolith/status/KNOWLEDGE_FEDERATION.md)

## 🛠️ CLI Operations (`scripts/registry_engine.py`)

```bash
# Show summary statistics across all domains
python3 /root/.agents/skills/library-of-links/scripts/registry_engine.py summary

# Search for authorities by keyword, tag, or domain
python3 /root/.agents/skills/library-of-links/scripts/registry_engine.py query -q "orbital"
python3 /root/.agents/skills/library-of-links/scripts/registry_engine.py query --domain physics
python3 /root/.agents/skills/library-of-links/scripts/registry_engine.py query --tag "genomics"

# Add a new curated authority with provenance
python3 /root/.agents/skills/library-of-links/scripts/registry_engine.py add \
  --domain engineering_dev \
  --subdomain distributed_systems \
  --title "The Raft Consensus Algorithm" \
  --url "https://raft.github.io/" \
  --description "Understandable Distributed Consensus protocol specification and visualizations." \
  --tags distributed consensus raft algorithms \
  --source "Stanford & GitHub"

# Verify URL liveness
python3 /root/.agents/skills/library-of-links/scripts/registry_engine.py verify

# Export to Markdown for Monolith status board
python3 /root/.agents/skills/library-of-links/scripts/registry_engine.py export --format markdown --output /data/data/com.termux/files/home/monolith/status/KNOWLEDGE_FEDERATION.md
```
