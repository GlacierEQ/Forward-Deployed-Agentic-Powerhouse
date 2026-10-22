---
name: apex-mega-repo-forge
description: Autonomous Mega-Repository Synthesis Engine ("The Lincoln Log Pipeline"). Takes an idea, harvests proven open-source blueprints from GitHub, synthesizes a cohesive full-stack Next.js/FastAPI Mega-Repo, and verifies tests on cloud runners.
version: 4.0.0
status: active
---

# APEX Mega-Repo Forge — "The Lincoln Log Pipeline"

The **APEX Mega-Repo Forge** transforms high-level operator intent into complete, tested, production-ready full-stack software repositories.

## Operating Philosophy

Instead of writing repetitive boilerplate from scratch or hallucinating unstable patterns, the Forge:
1. **Searches GitHub:** Discovers the highest-starred, battle-tested open-source repositories matching each pillar of the mission.
2. **Extracts "Lincoln Logs":** Isolates proven modular patterns (FastAPI async routers, Pydantic v2 schemas, Next.js 15 Tailwind UI, Docker Compose, GitHub Actions CI/CD).
3. **Synthesizes Cohesive Organisms:** Merges the Lincoln Logs into a unified Mega-Repository with zero placeholder comments, zero fake execution, and strict TypeScript/Python type safety.
4. **Enforces Epistemic Verification (L0–L5):** Validates syntax, compiles all source code, executes automated unit tests, and records SHA-256 fingerprints in `FORGE_SYNTHESIS_RECEIPT.json`.

---

## CLI Usage

### 1. Plant an Idea, Synthesize, and Deploy Directly to GitHub
```bash
python3 /root/engine_forge/mega_repo_forge.py \
  --mission "Autonomous Legal Discovery & Timeline Forensics Suite" \
  --name "apex-legal-forensics-suite" \
  --profile legal \
  --push
```
*Creates the repository under `GlacierEQ/apex-legal-forensics-suite`, runs epistemic tests, commits, pushes, and triggers Ubuntu cloud CI/CD automatically.*

### 2. Multi-Agent Swarm Orchestration Engine
```bash
python3 /root/engine_forge/mega_repo_forge.py \
  --mission "Decentralized Swarm Intelligence & MCP Constellation Router" \
  --name "apex-swarm-constellation" \
  --profile swarm \
  --push
```

### 3. Quantitative Trading & Risk Governor
```bash
python3 /root/engine_forge/mega_repo_forge.py \
  --mission "Real-time Order Execution & Portfolio Risk Engine" \
  --name "apex-quant-engine" \
  --profile quant \
  --push
```

### 4. Custom Lincoln Log Probing
```bash
python3 /root/engine_forge/mega_repo_forge.py \
  --mission "Distributed AI Audio Transcription & Diarization Engine" \
  --domains "whisper faster-whisper fastapi-template nextjs-dashboard" \
  --name "apex-whisper-forensics-suite"
```

---

## Generated Repository Architecture

Every synthesized Mega-Repository strictly conforms to the APEX Engineering Standard:

```
<project-name>/
├── README.md                      # Architecture, Lincoln-Log lineage & quickstart
├── apex.capabilities.yaml         # Machine-readable APEX capability manifest
├── docker-compose.yml             # Multi-stage containerized deployment
├── Makefile                       # Standardized test, lint, and run targets
├── .gitignore                     # Production ignore rules
├── FORGE_SYNTHESIS_RECEIPT.json   # Cryptographic SHA-256 verification ledger
├── backend/
│   ├── Dockerfile                 # Slim Python 3.12 container
│   ├── requirements.txt           # Pinned core dependencies
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py                # FastAPI async endpoints & Pydantic models
│   └── tests/
│       ├── __init__.py
│       └── test_api.py            # Automated unit tests (100% pass required)
├── frontend/
│   ├── package.json               # Next.js 15, React 18, Tailwind, Lucide
│   ├── tsconfig.json              # Strict TypeScript configuration
│   ├── tailwind.config.js         # APEX Dark Theme palette
│   └── src/
│       └── app/
│           ├── globals.css        # Tailwind directives
│           ├── layout.tsx         # Responsive root layout
│           └── page.tsx           # Interactive real-time dashboard UI
└── .github/
    └── workflows/
        └── ci.yml                 # Automated cloud runner CI/CD (ubuntu-latest)
```

---

## Epistemic Verification Contract

* **L0 (Provenance):** SHA-256 calculated and logged for every created file.
* **L1 (Unit Gates):** Zero mock sleep statements; real cryptographic and functional validation.
* **L2 (Type Safety):** Full type contract between frontend TypeScript interfaces and backend Pydantic models.
* **L3 (Substrate Leverage):** Fast async execution optimized for Linux/Ubuntu containers.
* **L4 (Invariant):** Operator testimony protected under FRE 601/602 in all evidence ingestion pipelines.
* **L5 (Mesh Swarm):** Docker and GitHub Actions cloud runner compatibility out of the box.
