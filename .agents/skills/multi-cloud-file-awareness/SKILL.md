---
name: multi-cloud-file-awareness
description: Safely ingest, index, and process multi-cloud file sources (OneDrive, Dropbox, Google Drive) with PII filtering.
---

# Multi-Cloud & Multi-Account File Awareness Skill

## 1. Scope & Authority
Enforces the 18-Point Multi-Cloud Capability and Multi-Account Governance Addendum across all agents and connectors operating on cloud files.

## 2. Core Execution CLI
```bash
# Ingest single file and generate standard JSON
multi-cloud-awareness ingest <file_path> [--account <alias>] [--risk <low|medium|high>]

# Bulk scan and catalog a cloud folder or local path
multi-cloud-awareness scan <directory> [--limit <n>]

# View active catalog records in SQLite WAL
multi-cloud-awareness catalog [--limit <n>]

# Run full unit and integration test suite
multi-cloud-awareness test
```

## 3. Mandatory JSON Contract (Rule 12 + Addendum A)
Every file ingestion result or policy decision MUST output this schema:
```json
{
  "file_id": "<string>",
  "source_platform": "<string>",
  "path": "<string>",
  "owner": "<string>",
  "ingestion_timestamp": "<ISO8601>",
  "checksum": "<string>",
  "mime_type": "<string>",
  "size": 0,
  "version": "<string>",
  "sensitivity_label": "<NONE|PII|CONFIDENTIAL|RESTRICTED>",
  "trust_score": 0.0,
  "action_taken": "<INGESTED|REDACTED|QUARANTINED|BLOCKED>",
  "reason": "<string>",
  "lineage_id": "<string>",
  "account_id": "<string>",
  "account_alias": "<string>",
  "account_type": "<EnterpriseManaged|Business|Personal|SharedDrive|ServiceAccount>",
  "tenant_id": "<string>",
  "account_owner": "<string>",
  "account_email": "<string>",
  "account_role": "<string>",
  "account_region": "<string>",
  "account_trust_score": 0.0,
  "account_status": "<Active|Suspended|Unlinked|PendingConsent>"
}
```

## 4. Trust & Sandboxing Rules
- **Enterprise Managed**: SharePoint / Box Enterprise (Base trust: 0.90 + 0.20 SSO = 1.0)
- **Business Tier**: OneDrive Business / Google Workspace / Dropbox Business (Base trust: 0.70 + 0.15 = 0.85)
- **Consumer / Low Trust**: iCloud / Terabox / Consumer accounts (Base trust: 0.40 - 0.40 = 0.0 -> Sandboxed)
- **Sandbox Gate**: Any asset with `trust_score < 0.60` is quarantined until explicit validation occurs.
- **PII Gate**: Deterministic or regex match with confidence $\ge 0.85$ requires auto-redaction (low-risk), JIT quarantine (medium-risk), or immediate block (high-risk model).

## 5. Storage Layer
- Master Catalog Database: `/data/data/com.termux/files/home/.openclaw/state/multi_cloud_catalog.sqlite` (SQLite WAL mode).
