---
name: apex-bootup-supreme
description: Comprehensive bootup skill that activates all key vaults, memory clusters, local storage mounts, cloud drives, and PRoot/Localhost hybrid bridges.
---

# APEX Bootup Supreme Skill (Merged into APEX Sovereign Supreme)

This skill provides full-spectrum activation of your entire infrastructure across both PRoot (Ubuntu glibc container) and native Localhost (Termux).

> [!NOTE]
> This skill has been merged into the master **`apex-sovereign-supreme`** skill suite.

## Activated Infrastructure Layers

1. **Key Vaults & Secrets**:
   - `~/.operator_key_vault/gatekeeper.env`
   - `~/.apex_vault/credentials.env`
   - `/data/data/com.termux/files/home/MISSIONS/CONSOLIDATED/INFRASTRUCTURE/APEX/key_vault`
   - Auto-exports `GEMINI_API_KEY`, `GOOGLE_API_KEY`, `GROQ_API_KEY`, `ANTHROPIC_API_KEY`.

2. **Memory Clusters & Service Nodes**:
   - **APEX Connector Gateway** (`127.0.0.1:9000`)
   - **APEX Device RPC Bridge** (`127.0.0.1:8990`)
   - **Holographic Mesh Proxy** (`127.0.0.1:8999`)
   - **Apex Memory Bridge** (`127.0.0.1:8787`)
   - **Nexus API Server** (`127.0.0.1:8002`)
   - **Apex Router** (`127.0.0.1:8003`)
   - **Mastermind API** (`127.0.0.1:8741`)
   - **Qdrant Vector Database** & **Neo4j Knowledge Graph**

3. **Storage & Cloud Drive Activation**:
   - **Local Storage**: `/sdcard` (Android Shared Storage), `/data/data/com.termux/files/home/storage`, `/root` (PRoot System Root).
   - **Cloud Storage**: Dropbox Distillation, Google Drive / Cloud Cases, Notion Workers Mesh.

4. **Execution Protocol**:
   To run the complete supreme bootup diagnostics and activation:
   ```bash
   python3 /root/.agents/skills/apex-sovereign-supreme/scripts/bootup_runner.py
   ```
