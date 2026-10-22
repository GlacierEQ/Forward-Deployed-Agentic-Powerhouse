---
name: cloud-filesystem-expert
description: Multi-cloud file awareness, Aspen-Grove pointer indexing, and evidence lifecycle.
---

# Skill: cloud-filesystem-expert

# APEX Cloud Filesystem Expert — Hierarchical Skill v1.0.0

**Status:** ENFORCED / ACTIVATED  
**Scope:** Multi-cloud file awareness, Aspen-Grove pointer indexing, APEX_DRIVE hierarchy, evidence lifecycle, cloud bridge orchestration.  
**Governance:** Holographic Mesh (decentralized, multi-node, no single winner).

---

## 1. Native Integration Map

Composes these skills directly:
- [`multi-cloud-file-awareness`](file:///root/.agents/skills/multi-cloud-file-awareness/SKILL.md) — ingestion, catalog, PII gate
- [`aspen-grove-core`](file:///root/.agents/skills/aspen-grove-core/SKILL.md) — pointer indexing, quantum graph
- [`token-optimizer`](file:///root/.agents/skills/token-optimizer/SKILL.md) — compression, tier routing, disk offloading
- [`max-token-saver`](file:///root/.agents/skills/max-token-saver/SKILL.md) — 5-step process enforcement
- [`casebuilder-allegation-forge`](file:///root/.agents/skills/casebuilder-allegation-forge/SKILL.md) — evidence architecture
- [`apex-litigation-colossus`](file:///root/.agents/skills/apex-litigation-colossus/SKILL.md) — case packages

CLI Tools:
- `/root/apex_case_framework/cloud_bridge.py` — WebDAV bridge (`mega_cloud:` on 127.0.0.1:8088)
- `/root/apex_case_framework/multi_cloud_file_awareness.py` — catalog CLI (`ingest`, `scan`, `catalog`, `test`)
- `/root/computer-user/case_brain/jack_the_ripper_casebuilder.py` — ledger, seed, pleading, referral, test
- `/root/apex_case_framework/apex_litigation_colossus_engine.py` — 7-pillar case build engine

---

## 2. Cloud Topology (Live State)

| Remote | Type | Trust Score | Status | Notes |
|--------|------|-------------|--------|-------|
| `gdrive:` | OAuth (shared client_id — deprecated 2026) | 0.70 | ✅ Connected (quota: 3.0 TB free) | Active case work |
| `gdrive_glacier_sa:` | Service Account (glacier) | 1.00 | ✅ Connected (no quota — needs shared drive) | Archives |
| `gdrive_casey_sa:` | Service Account (casey) | 1.00 | ✅ Connected (no quota) | FileBoss Inbox |
| `gdrive2-5:` | OAuth deprecated | 0.00 | ❌ Expired / deprecated | Must recreate client_id |
| `onedrive:` | OAuth (re-connected) | 0.85 | ✅ Connected | 5 root dirs |
| `dropbox:` | OAuth (re-connected) | 0.85 | ✅ Connected | 10 root dirs |
| `dropbox_aux_1:` | OAuth (scope limited) | 0.85 | ⚠️ Scope issue (`files.metadata.read` missing) | App Console fix needed |
| `dropbox_aux_2:` | OAuth (revoked) | 0.00 | ❌ Invalid token | Re-auth required |
| `r2:` | Cloudflare R2 (S3) | 1.00 | ✅ Empty / connected | Available for overflow |
| `local_evidence:` | `/sdcard/Documents/01_LEGAL_AND_CASE_EVIDENCE/` | 1.00 | ✅ 45,841 files organized | Ground truth |
| `local_termux:` | `/data/data/com.termux/files/home/` | 1.00 | ✅ Full estate | Termux home |

---

## 3. APEX_DRIVE Structure (Master Index)

Verified live at `gdrive:APEX_DRIVE/MASTER_INDEX.md` (synchronized to `gdrive_glacier_sa:`). All 6 active cases have complete 7-folder structure. Archives complete (`glacier_sa:`). Evidence centralized (`gdrive:`). Systems ops organized. Quarantine isolated (`CONFIDENTIAL`, `RESTRICTED`). Point table at `/tmp/aspen_grove_pointer_index.json` (2,370 files indexed).

---

## 4. Enforced Protocol

Every filesystem mutation passes L0→L5 verification ladder. Zero fake execution (no mocked integration, no synthetic success, no placeholder adapters). No single-winner authority (mesh vocabulary: elite/pro/Hard/G). Human vocabulary: elite · pro · Hard · G. Every claim backed by tool evidence (hash + readback + receipt). Every contradiction preserved explicitly. Every next continuation point preserved in output packet.

---

## 5. CLI Invocation Pattern

```bash
# Ingest and classify
python3 /root/apex_case_framework/multi_cloud_file_awareness.py scan <dir> --limit <n>

# Catalog verification
python3 /root/apex_case_framework/multi_cloud_file_awareness.py catalog --limit <n>
python3 /root/apex_case_framework/multi_cloud_file_awareness.py test  # 4/4 verification gates

# Cloud bridge
python3 /root/apex_case_framework/cloud_bridge.py start <remote>

# Case build
python3 /root/computer-user/case_brain/jack_the_ripper_casebuilder.py ledger
python3 /root/computer-user/case_brain/jack_the_ripper_casebuilder.py test

# Token optimization
python3 /root/.agents/skills/token-optimizer/scripts/token_optimizer_engine.py route --query <task>
```

---

Base directory: `file:///root/.agents/skills/activate_all_skills/` (amplification engine base) + `file:///root/computer-user/` (operational).