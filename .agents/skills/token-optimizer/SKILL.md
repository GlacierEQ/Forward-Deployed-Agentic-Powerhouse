---
name: token-optimizer
description: Context reduction engine enforcing pointer indexing, targeted range reading, and surgical mutations for 75-90% savings.
---

# APEX Token Optimizer & Context Engine v2.0 (Holographic Mesh)

**Status:** ENFORCED ALWAYS-ON  
**Framework:** Holographic Mesh / Aspen-Grove Pointer Indexing  
**Primary Goal:** Maximize coherent capability advance while achieving ~75%–90% token reduction across multi-turn sessions.

---

## 1. Core Operating Doctrine

The AI acts as an **efficient coordinator and surgical builder**, not a verbose text generator. All high-volume context, heavy research, and intermediate data are offloaded to disk artifacts, pointer tables, and background subagent swarms.

```
                    ┌──────────────────────────────────────────────┐
                    │      Operator Intent / High-Level Goal       │
                    └──────────────────────┬───────────────────────┘
                                           │
                        ┌──────────────────┴──────────────────┐
                        ▼                                     ▼
        ┌───────────────────────────────┐     ┌───────────────────────────────┐
        │ Dynamic Mesh Tier Routing     │     │ Context Compressor & Scrubber │
        │ (Tier 0 -> Tier 3 Allocator)  │     │ (Strips noise, saves ~50-80%) │
        └───────────────┬───────────────┘     └───────────────┬───────────────┘
                        │                                     │
                        └──────────────────┬──────────────────┘
                                           │
                    ┌──────────────────────▼───────────────────────┐
                    │   Aspen-Grove Pointer Indexer (@pointer:id)  │
                    │   (References SHA-256 / Blake2b hashes)      │
                    └──────────────────────┬───────────────────────┘
                                           │
       ┌───────────────────────────────────┼───────────────────────────────────┐
       ▼                                   ▼                                   ▼
┌──────────────┐                  ┌─────────────────┐                 ┌─────────────────┐
│ S хирургический│                  │ Parallel Swarm  │                 │ Disk Artifacts  │
│ Tool Guards  │                  │ Flash Subagents │                 │ & Point Tables  │
│ (Line bounds)│                  │ (Broad searches)│                 │ (Zero chat dump)│
└──────────────┘                  └─────────────────┘                 └─────────────────┘
```

---

## 2. Mandatory 5-Pillar Token Savings Protocol

### Pillar 1: Targeted Range Reading (Zero Full Dumps)
- **Rule:** Never execute an unbounded `view_file` on large files.
- **Enforcement:** Always supply explicit `StartLine` and `EndLine` parameters targeting only the specific function, class, or block under inspection.
- **Surgical Bounds:** Keep reads under 250 lines per tool call.

### Pillar 2: Surgical Mutations Over File Overwrites
- **Rule:** Prefer `replace_file_content` over full-file overwrites.
- **Enforcement:** Target only the precise contiguous block of lines that need modification.

### Pillar 3: Aspen-Grove Pointer Indexing vs Directory Flooding
- **Rule:** Use pointer index lookups instead of scanning massive directory trees repeatedly.
- **Enforcement:** Query `/tmp/aspen_grove_pointer_index.json` or run `token_optimizer_engine.py index` to generate Blake2b/SHA-256 pointer tables (`@pointer:<id>` or `ptr_<hash>`).

### Pillar 4: Subagent Delegation for Broad Searches
- **Rule:** Do not clutter root context with 50+ file searches or web crawling.
- **Enforcement:** Delegate exploratory codebase surveys, web scraping, and log triage to background subagents (`Model: flash`).

### Pillar 5: Disk & Artifact Offloading
- **Rule:** Never paste large raw data, massive logs, or full codebase extracts directly into conversational responses.
- **Enforcement:** Write substantial outputs to disk files or artifact markdown files in the session brain, outputting only compact markdown summaries and clickable file links.

---

## 3. Dynamic Mesh Execution Tiers

| Tier | Name | Target Engine / Model | Trigger Condition | Estimated Savings |
|:---:|:---|:---|:---|:---:|
| **Tier 0** | Local Fast Lite | Local / Python Script | Lookups, regex, line counts, pointer checks | **95%** |
| **Tier 1** | Free / Open Mesh | Fast Coder / Tools | Utility transforms, doc parsing, schema checks | **80%** |
| **Tier 2** | Fast Specialist Swarm | Flash / Subagent Swarm | Multi-file edits, unit test suites, repo scouting | **65%** |
| **Tier 3** | Heavy Reasoning Architect | Pro / High-Reasoning | System architecture, legal forensics, adversarial loops | **0% (Master Context)** |

---

## 4. CLI & Programmatic Tooling

The token optimizer engine is located at:
[`/root/.agents/skills/token-optimizer/scripts/token_optimizer_engine.py`](file:///root/.agents/skills/token-optimizer/scripts/token_optimizer_engine.py)

### Commands

```bash
# 1. Compress a file or text chunk
python3 /root/.agents/skills/token-optimizer/scripts/token_optimizer_engine.py compress --file path/to/file.py

# 2. Index a directory with Aspen-Grove pointers
python3 /root/.agents/skills/token-optimizer/scripts/token_optimizer_engine.py index --dir /root/computer-user --depth 3

# 3. Classify task tier
python3 /root/.agents/skills/token-optimizer/scripts/token_optimizer_engine.py route --query "search repository for memory connectors"

# 4. View cumulative token telemetry
python3 /root/.agents/skills/token-optimizer/scripts/token_optimizer_engine.py stats

# 5. Execute self-test suite
python3 /root/.agents/skills/token-optimizer/scripts/token_optimizer_engine.py test
```

---

## 5. Output Contract

1. **Compact Status First**: Direct, high-signal summary of actions taken and verified state.
2. **Clickable File Links**: Every modified or referenced file must use clickable GitHub markdown links (`[file_name](file:///absolute/path)`).
3. **No Narrative Fluff**: Eliminate empty transitional phrases.
4. **Definitive Next Step**: Conclude with a clear, actionable prompt or next milestone.
