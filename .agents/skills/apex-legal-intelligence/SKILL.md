---
name: apex-legal-intelligence
description: "Legal reasoning and forensics engine: 15-step pipeline, authority hierarchy, red-team simulation, and motion generation."
version: 1.0.0
status: active
---

# APEX Legal Intelligence — Mega-Skill 4

**Legal Reasoning & Forensics Engine** — Convert verified facts and authority into filing-ready artifacts that survive adversarial attack.

## Composed Sub-Skills

| Sub-Skill | Role | Entry Point |
|-----------|------|-------------|
| legal-automation-suite | Motion gen, RICO, FRCP, evidence, chain of custody, audit | `LegalAutomationEngine` class |
| digital-law-library-master | Evidence matrix, citation gate, court-safe tone, drift guard | `LL:*` modules |
| apex_sovereign_intelligence.py | 15-step pipeline, 5-front matrix, adversarial attack, authority | `SovereignIntelligenceEngine` class |
| aspen-grove-core | Pointer-indexed persistence, quantum memory, SHA-256, auto-heal | `aspen-grove-core` skill |
| evidence-authenticator | Provenance chains, custody notes, authenticity verdicts | `evidence_authenticator.py` (new) |
| contradiction-hunter | Cross-source conflict detection | `contradiction_hunter.py` (new) |

## Unified Capabilities (apex.capabilities/v1)

```yaml
schema: apex.capabilities/v1
repository: GlacierEQ/Pro-DOCTOR-STRANGE
mega_skill: apex-legal-intelligence
capabilities:
  - id: legal.reason
    description: Execute full 15-Step APEX Legal Reasoning Pipeline (objective → remedy)
    entrypoint: apex_sovereign_intelligence.py reason
    interface: cli|library|http
    inputs:
      - name: objective
        type: string
        required: true
      - name: front_id
        type: string
        enum: [FRONT_1, FRONT_2, FRONT_3, FRONT_4, FRONT_5]
        default: FRONT_1
    outputs:
      - name: reasoning_stack
        type: object
      - name: confidence_score
        type: number
    dependencies: [legal-automation-suite, digital-law-library-master, aspen-grove-core]
    confidence: verified

  - id: legal.attack
    description: Adversarial red-team stress test against proposed theory/filing
    entrypoint: apex_sovereign_intelligence.py attack
    interface: cli|library|http
    inputs:
      - name: theory
        type: string
        required: true
    outputs:
      - name: attack_vectors
        type: array
      - name: overall_survival_rating
        type: string
    dependencies: [legal-automation-suite, digital-law-library-master]
    confidence: verified

  - id: legal.authority
    description: Lookup binding authority (constitution, statute, rule, precedent) by topic
    entrypoint: apex_sovereign_intelligence.py authority
    interface: cli|library|http
    inputs:
      - name: topic
        type: string
        required: true
        enum: [due_process_voidness, judicial_disqualification, federal_rico_civil, section_1983_conspiracy]
    outputs:
      - name: authorities
        type: object
    dependencies: []
    confidence: verified

  - id: legal.research
    description: Deep legal research with authority hierarchy
    entrypoint: digital-law-library-master:LL:EVIDENCE_MATRIX + LL:CITATION_GATE
    interface: library|http
    inputs:
      - name: query
        type: string
      - name: jurisdiction
        type: string
        enum: [federal, hawaii, ninth_circuit]
      - name: authority_level_min
        type: string
        enum: [constitution, statute, rule, binding_precedent, persuasive_precedent]
    outputs:
      - name: results
        type: array
    dependencies: [digital-law-library-master]

  - id: legal.automate
    description: Generate FRCP-compliant motions, complaints with citation verification
    entrypoint: legal-automation-suite:LegalAutomationEngine
    interface: library|http
    inputs:
      - name: motion_type
        type: string
        enum: [motion_to_compel, motion_to_dismiss, section_1983_complaint, rico_complaint, injunction_motion, motion_for_vacatur, motion_for_disqualification]
      - name: case_id
        type: string
      - name: facts
        type: array
        items: {type: string}
      - name: authorities
        type: array
        items: {type: string}
    outputs:
      - name: document
        type: string
      - name: citation_report
        type: object
    dependencies: [legal-automation-suite, digital-law-library-master]
    confidence: verified

  - id: evidence.ingest
    description: Ingest evidence with SHA-256 hashing, Daubert compliance, certification
    entrypoint: legal-automation-suite:ForensicEvidenceEngine
    interface: library|http
    inputs:
      - name: file_path
        type: string
      - name: case_id
        type: string
      - name: source
        type: string
        enum: [digital_forensics, court_filing, witness_statement, expert_report, financial_record, phone_record]
      - name: description
        type: string
    outputs:
      - name: exhibit
        type: object
        properties:
          hash: {type: string, pattern: "^sha256:"}
          certified: {type: boolean}
          daubertCompliant: {type: boolean}
    dependencies: [legal-automation-suite, aspen-grove-core]

  - id: evidence.chain
    description: Record and retrieve chain of custody transfers
    entrypoint: legal-automation-suite:ChainOfCustodyEngine
    interface: library|http
    inputs:
      - name: evidence_id
        type: string
      - name: from_custodian
        type: string
      - name: to_custodian
        type: string
      - name: timestamp
        type: string
        format: date-time
      - name: purpose
        type: string
    outputs:
      - name: chain
        type: array
    dependencies: [legal-automation-suite]

  - id: evidence.authenticate
    description: Build provenance envelope, verify authenticity, detect tampering
    entrypoint: aspen-grove-core + evidence_authenticator.py
    interface: library|http
    inputs:
      - name: exhibit_id
        type: string
      - name: original_source
        type: string
      - name: transformations
        type: array
        items:
          type: object
          properties:
            method: {type: string}
            tool: {type: string}
            confidence: {type: number}
    outputs:
      - name: verdict
        type: object
        properties:
          authenticity_status: {type: string, enum: [ORIGINAL, CERTIFIED_COPY, TRANSCRIPTION, SUMMARY, UNSUPPORTED]}
          provenance_chain: {type: array}
          tamper_detected: {type: boolean}
          sha256_match: {type: boolean}
    dependencies: [aspen-grove-core, legal-automation-suite]

  - id: timeline.build
    description: Build source-linked event chronology with contradiction detection
    entrypoint: aspen-grove-core + contradiction_hunter.py
    interface: library|http
    inputs:
      - name: case_id
        type: string
      - name: sources
        type: array
        items:
          type: object
          properties:
            type: {type: string, enum: [docket, transcript, exhibit, declaration, order, metadata, communication]}
            path: {type: string}
            date_range: {type: string}
    outputs:
      - name: chronology
        type: array
      - name: contradiction_matrix
        type: array
    dependencies: [aspen-grove-core]

  - id: case.fronts
    description: Query the 5-front master litigation matrix
    entrypoint: apex_sovereign_intelligence.py case_fronts
    interface: cli|library|http
    inputs:
      - name: front_id
        type: string
        enum: [FRONT_1, FRONT_2, FRONT_3, FRONT_4, FRONT_5, ALL]
        default: ALL
    outputs:
      - name: fronts
        type: object
    dependencies: []
    confidence: verified
```

## CLI Interface

```bash
apex-legal <command> [options]

# Core reasoning (WORKING NOW via apex_sovereign_intelligence.py)
apex-legal reason --objective "Due Process Vacatur" --front FRONT_1
apex-legal attack --theory "Federal RICO Injunction"
apex-legal authority --topic judicial_disqualification
apex-legal fronts --front ALL

# Motion generation (wires to legal-automation-suite)
apex-legal automate --motion motion_for_vacatur --case 1FDV-23-0001009 --facts facts.json

# Evidence lifecycle (wires to legal-automation-suite + aspen-grove-core)
apex-legal evidence ingest --file exhibit.pdf --case 1FDV-23-0001009 --source court_filing --desc "Motion to Vacate"
apex-legal evidence chain --evidence EX-001 --from "Lab" --to "Attorney" --purpose "Review"
apex-legal evidence authenticate --exhibit EX-001 --source original --transforms transforms.json

# Timeline & chronology (wires to aspen-grove-core + contradiction-hunter)
apex-legal timeline build --case 1FDV-23-0001009 --sources sources.json
```

## Verification Gates

| Gate | Test | Pass Criteria |
|------|------|---------------|
| G1 | `reason` on known issue | Confidence ≥ 0.95; all 15 steps populated |
| G2 | `attack` on generated theory | Survival ≥ 95%; no CRITICAL unaddressed |
| G3 | `authority` lookup | Returns binding authorities with pin-cites |
| G4 | `automate` motion generation | FRCP compliant; citations verified by LL:CITATION_GATE |
| G5 | `evidence.ingest` → hash → validate | SHA-256 match; tamper detection works |
| G6 | `timeline.build` from known sources | Zero hallucinations; all events source-linked |
| G7 | Cross-front consistency | No contradictory positions across FRONT_1-5 |