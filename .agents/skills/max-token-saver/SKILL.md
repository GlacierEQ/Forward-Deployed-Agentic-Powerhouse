---
name: max-token-saver
description: "Maximum token saving: persistent memory, Aspen-Grove pointer compression, and subagent swarm offloading."
---

# MAX-TOKEN-SAVER v2.0 — Holographic Mesh Edition

**Status:** ACTIVE / ALWAYS-ON  
**Topology:** Holographic Mesh (Decentralized, Multi-Node)  
**Primary Objective:** Maximize coherent advance with near-100% token efficiency.

---

## 1. Purpose

Ultra-efficient orchestration layer. The AI acts as coordinator and surgical executor, not a bloated content generator. Forces heavy tool use, memory activation, pointer-indexed compression, parallel execution, and distributed processing.

---

## 2. Enforced 5-Step Process (Execute in Order)

1. **Memory First**
   - Query or reference persistent stores (Supabase, Supermemory, Mem0, local files, Aspen-Grove pointer index) before generating text.
   - Summarize only the exact delta required.

2. **Tool & MCP Discipline**
   - Prefer surgical tool queries (`grep_search`, `find_by_name`, targeted `view_file` ranges) over speculative conversational generation.

3. **Parallel & Distributed Swarms**
   - Fire multiple tool calls in one step.
   - Route heavy analysis, deep codebase surveys, and evidence aggregation to background subagents (`Model: flash`).

4. **Offload to Files & Artifacts**
   - Write substantial codebases, datasets, and diffs to disk via `write_to_file` or markdown artifacts.
   - Never paste long, repetitive payloads into chat responses.

5. **Minimize & Reference**
   - Use compact formats (bullets, tables, JSON summaries, pointer hashes, file links).
   - Reference existing artifacts and pointer IDs (`@pointer:<id>`) instead of re-quoting them.

---

## 3. Truth & Output Contract

- **Compact Status First**: Status + key references + clickable file paths.
- **Heavy Content in Files**: Zero chat pollution.
- **Verification Before Claims**: Pass L0–L5 epistemic gates on all code and state mutations.
- **Conclude Cleanly**: State exact next task or milestone.

---

## 4. Integration

Binds natively to [`token-optimizer`](file:///root/.agents/skills/token-optimizer/SKILL.md), [`aspen-grove-core`](file:///root/.agents/skills/aspen-grove-core/SKILL.md), and [`apex-sovereign-supreme`](file:///root/.agents/skills/apex-sovereign-supreme/SKILL.md).

CLI Engine: [`/root/.agents/skills/token-optimizer/scripts/token_optimizer_engine.py`](file:///root/.agents/skills/token-optimizer/scripts/token_optimizer_engine.py)
