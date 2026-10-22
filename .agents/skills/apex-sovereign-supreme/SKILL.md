---
name: apex-sovereign-supreme
description: Master skill uniting bootup, Smithery 32+ MCP mesh connectors, token optimizer, device API, and auto-healing runtime.
---

# APEX Sovereign Supreme Master Skill Suite

The **APEX Sovereign Supreme** skill suite is the single unified operating engine for all agent capabilities across PRoot Ubuntu container and native Termux host environment.

## Integrated Skill Pillars

### 1. 🚀 Supreme Bootup & Vault Activation (`bootup_supreme`)
- **Key Vault Exports**: Automatically loads `.operator_key_vault/gatekeeper.env`, `.apex_vault/credentials.env`, `apex-mimo.env`, and OAuth tokens.
- **Environment Exports**: `GEMINI_API_KEY`, `GOOGLE_API_KEY`, `GROQ_API_KEY`, `ANTHROPIC_API_KEY`.
- **Infrastructure Startup**: Auto-launches and verifies Memory Bridge (8787), Mastermind API (8741), Nexus API (8002), Apex Router (8003), Qdrant Vector DB, and Neo4j.

### 2. 📱 Full Device Function & Access (`device_full_access`)
- **Hardware Telemetry & Control**: Real-time access to Android battery health, temperature, voltage, charging state, CPU load, and RAM stats.
- **Sensors & Location**: Query GPS / Network location, accelerometer, light, proximity, gyroscope.
- **Media & Hardware Functions**: Take camera photos (`camera_photo`), Flashlight (`torch`), Haptic vibration (`vibrate`), Text-to-Speech synthesis (`tts_speak`), Audio volume control (`volume`).
- **User Interface & Signals**: Post system notifications (`notification`), Android toast popups (`toast`), Clipboard get/set (`clipboard`).
- **Network & Connectivity**: Wi-Fi connection telemetry, Wi-Fi scanner, Cell carrier info.
- **Host Execution & Storage**: Access `/sdcard`, PRoot filesystem, Termux home storage, and native host command bridge (`exec_host_command`).
- **HTTP RPC Endpoint**: Live JSON-RPC & REST service on `http://127.0.0.1:8990`.

### 3. 🌐 Supreme Connector Hub & Smithery Mesh (`connector_hub`)
- **32+ Active MCP Servers**: Integrated access to GitHub, HuggingFace, Google Drive/Docs/Sheets/Gmail/Photos, Notion, Dropbox, OneDrive, Exa Search, Tavily, Jina AI, DeepWiki, Case Law Search, Lex Oracle, Omega Memory, LiveDataLink.
- **Unified Gateway**: Operates on `http://127.0.0.1:9000` with response caching, connection pooling, and search toolbox (`search_toolbox`).
- **Multi-Protocol Router**: Seamless bridge between REST, JSON-RPC 2.0, local Python APIs, and TCP socket interfaces.

### 4. ⚡ Maximum Runtime & Auto-Healing Engine (`runtime_optimizer`)
- **Auto-Healing Watchdog**: Daemon mode continuously checks and resurrects offline service ports (8990, 9000, 8999, 8787, 8741, 8002, 8003) every 30 seconds.
- **Resource Governor**: Log file rotation, RAM memory reclamation, process priority management (`nice`/`renice`).
- **Low-Latency Caching**: Accelerated tool lookup definitions and schema metadata caching to guarantee sub-second execution speeds.

### 5. 📉 Context & Token Optimizer (`token_optimizer`)
- **Targeted Code Viewing**: Enforces `view_file` with explicit `StartLine` and `EndLine` constraints.
- **Lossless Edits**: Prefers `replace_file_content` and `multi_replace_file_content` over costly full-file rewrites.
- **Subagent Parallelization**: Delegates heavy background search or research tasks to specialized subagents.

### 6. 🧠 Sovereign Intelligence & Adversarial Engine (`sovereign_intelligence`)
- **15-Step APEX Legal Reasoning Pipeline**: Fully automated issue-to-remedy structured evaluation.
- **Authoritative Hawaii & Federal Statutory Knowledge Graph**: Binding citations for Due Process voidness, mandatory disqualification, Civil RICO, and § 1983.
- **Master 5-Front Forensic Matrix**: Pre-indexed intelligence for 1FDV-23-0001009, 1FDA-23-0000515, Federal RICO, The Cataclysm Forensics, and Recovery.
- **Adversarial Red-Team Simulator**: Automated stress-testing of filings against hostile opposing counsel theories and judicial defenses.

---

## Direct CLI Commands & Utility Scripts

```bash
# 1. Complete Unified Bootup Diagnostic & Activation
python3 /root/.agents/skills/apex-sovereign-supreme/scripts/bootup_runner.py

# 2. Complete End-to-End System Operation Verification (14 Tests)
python3 /root/.agents/skills/apex-sovereign-supreme/scripts/verify_full_system_operation.py

# 3. Sovereign Intelligence & 15-Step Adversarial Reasoning
python3 /root/.agents/skills/apex-sovereign-supreme/scripts/apex_sovereign_intelligence.py reason --issue "Due Process Void Orders"
python3 /root/.agents/skills/apex-sovereign-supreme/scripts/apex_sovereign_intelligence.py attack --theory "Federal Civil RICO Injunction"
python3 /root/.agents/skills/apex-sovereign-supreme/scripts/apex_sovereign_intelligence.py authority --topic "judicial_disqualification"

# 4. Complete Device Control & Telemetry
python3 /root/.agents/skills/apex-sovereign-supreme/scripts/device_access_supreme.py battery
python3 /root/.agents/skills/apex-sovereign-supreme/scripts/device_access_supreme.py toast -m "APEX Sovereign Active"
python3 /root/.agents/skills/apex-sovereign-supreme/scripts/device_access_supreme.py system_info

# 5. Connector Gateway Status & Search
python3 /root/.agents/skills/apex-sovereign-supreme/scripts/connector_hub_supreme.py status
python3 /root/.agents/skills/apex-sovereign-supreme/scripts/connector_hub_supreme.py search -q "github"

# 6. Runtime Performance & Auto-Healing Resurrect
python3 /root/.agents/skills/apex-sovereign-supreme/scripts/runtime_optimizer_supreme.py heal
python3 /root/.agents/skills/apex-sovereign-supreme/scripts/runtime_optimizer_supreme.py daemon
```
