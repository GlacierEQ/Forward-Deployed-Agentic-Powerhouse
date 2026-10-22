# Long-Horizon Phase Playbooks (lazy-loaded)

This document is intentionally heavy. Load it only when executing a real
long-horizon campaign. The `SKILL.md` framework modules are the executable
surface; this is the strategic depth behind them.

## Phase 1 — Deep Time Memory (Aspen Grove Integration)
- **Problem:** `DualLayerMemoryBridge` holds state during one Swarm execution,
  but context dies when the Python process exits.
- **Mechanism:** Route `computer-user/LEDGERS/` output into an Aspen-Grove local
  vector store (or Supabase pgvector). Future VPs query the index by pointer,
  never by re-reading whole repos.
- **Pointer Indexing contract:** store a stable ID + SHA-256 digest, keep full
  content retrievable via the pointer. See `framework/long_horizon.py`.
- **Outcome:** an agent spawned months later mounts the exact execution state
  established today.

## Phase 2 — Unattended Legal Forensics (Background Swarm)
- **Mechanism:** bind a scheduled worker to the Trinity Daemon (port 8741) and a
  clock daemon. Nightly docket sweeps hit court/PACER APIs.
- **Contradiction hunting:** on a new docket, a disposable worker cross-references
  it against `SUPERLUMINAL_CASE_MATRIX` and `1FDV-23-0001009` timelines.
- **Outcome:** operator wakes to a targeted, reviewed draft — not raw noise.

## Phase 3 — The High Council (Hierarchical Expansion)
- **Mechanism:** Mastermind spawns three VPs — Procedural Strategist, Evidence
  Authenticator, System Architect. They debate in a hidden token-saving loop,
  resolve contradictions, *then* dispatch Store Managers.
- **Adjudication:** weighted by authority + provenance; unresolved uncertainty is
  preserved explicitly. See `framework/high_council.py`.
- **Outcome:** a self-correcting strategic brain that prevents single-point logic
  failure before heavy execution.

## Phase 4 — Hardware & OS Resilience (The Sovereign Fortress)
- **Auto-healing:** if Termux is killed by Android battery management,
  `apex-boot-core` re-establishes port 8741, remounts the memory bridge, and
  resumes the interrupted worker.
- **Local fallback mesh:** if GitHub/Supabase drop, the swarm falls back to local
  SQLite + offline LLM inferencing via Smithery Mesh.
- **Outcome:** survives power cycles, network blackouts, and OS kills without
  losing a single execution hash.

> "Governance serves progress. Progress does not serve governance." — AGENTS.md
