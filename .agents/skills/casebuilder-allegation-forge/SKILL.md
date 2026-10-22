---
name: casebuilder-allegation-forge
description: Engine transforming chaotic evidence, records, and filings into structured allegations and proof matrices.
---

# JACK THE RIPPER / CASEBUILDER / ALLEGATION FORGE

**Status:** ENFORCED IN APEX CONTROL PLANE  
**Engine:** [`jack_the_ripper_casebuilder.py`](file:///root/computer-user/case_brain/jack_the_ripper_casebuilder.py)  
**Prime Directive:** *«TURN EVERY MATERIAL EVENT INTO A PROPOSITION THAT CAN BE PROVEN, ATTACKED, STRENGTHENED, AND USED.»*

---

## 1. Operating Doctrine

Jack does not merely destroy hostile structure. Jack builds the case that replaces it.
Every material event is systematically decomposed:

```
INCIDENT
  │
  ├── DECOMPOSED EVENTS (14 parameters: Who, Act, Date, Location, Words/Conduct, 
  │                       Authority Asserted vs Existed, Restraint, Searches, 
  │                       Property, Records Created, Aftermath, Harm)
  │
  ├── ACTOR DOSSIERS (Known Acts, Statements, Signed Docs, Notices Received,
  │                   Unknown Actor 01 Hunting Targets: Duty rosters, CAD, badge logs)
  │
  ├── INSTITUTION DOSSIERS (Policies, Systems, Complaint History, Supervisory Structure)
  │
  ├── 6-LANE ALLEGATION FORGE:
  │     ├── Factual Misrepresentation
  │     ├── Procedural Violation
  │     ├── Ethical Violation
  │     ├── Civil Wrong
  │     ├── Administrative Misconduct
  │     └── Potential Criminal Theory
  │
  ├── ELEMENT MATRICES (Proven | Supported | Disputed | Missing)
  │
  ├── PROOF STACKING & SOURCE HIERARCHY (Contemporaneous > Later | Original > Derivative | Independent > Self-Serving)
  │
  ├── CONTRADICTION & IMPEACHMENT FUEL (Official claim vs Evidence -> Impeachment -> Knowledge -> Discovery)
  │
  ├── KNOWLEDGE & INTENT BUILD (What did they know? When? What did they do after knowing?)
  │
  ├── CAUSATION & DAMAGES FORGE (10 Harm categories, exact economic calculations & trebling)
  │
  ├── STEELMANNED DEFENSE FORGE & KILL TEST (10-Point Adversarial Attack -> Rebuttal or Kill)
  │
  ├── DISCOVERY ENGINE ("What document should exist if their story is true?")
  │
  ├── CROSS-EXAMINATION ARCHITECTURE (Lock Question -> Follow-Up -> Exit Block)
  │
  └── OUTPUT CONVERTERS:
        ├── Court-Ready Pleadings (Counts, Elements, Causation, Prayer)
        ├── Agency Referral Memoranda (Investigative handover briefs)
        ├── Procedural Motions (Vacatur, Disqualification, Compel, Sanctions)
        └── 12 Master Ledgers
```

---

## 2. Minimum Allegation Structure

```
ACTOR + ACT + DATE/PERIOD + LOCATION/CONTEXT + DUTY/PROHIBITION + FACTUAL BASIS + SOURCE BASIS + CONSEQUENCE
                                    ↓
                               [ALLEGATION]
                                    ↓
+ CORROBORATION + CONTRADICTION + KNOWLEDGE + PATTERN + MATERIALITY + HARM
                                    ↓
                          [SOLIDIFIED ALLEGATION]
```

---

## 3. Promotion States & Tiers

### Allegation Tiers
- **Tier 1 (Directly Proven)**: Ironclad anchor allegations with zero missing elements and direct authenticated primary records.
- **Tier 2 (Strongly Corroborated)**: Primary attack lanes supported by multiple converging independent sources.
- **Tier 3 (Supported Inference)**: Supported by factual chains and knowledge inferences.
- **Tier 4 (Plausible / Development)**: Missing elements flagged for immediate discovery retrieval.
- **Tier 5 (Speculative)**: Quarantined until documentary evidence arrives.

### Promotion States
`RAW` $\rightarrow$ `STRUCTURED` $\rightarrow$ `SOURCED` $\rightarrow$ `CORROBORATED` $\rightarrow$ `ELEMENT_MAPPED` $\rightarrow$ `DEFENSE_TESTED` $\rightarrow$ `HARDENED` $\rightarrow$ `PLEADING_READY` $\rightarrow$ `REFERRAL_READY` $\rightarrow$ `TRIAL_READY`

---

## 4. CLI & Control Plane Commands

Master Script: [`/root/computer-user/case_brain/jack_the_ripper_casebuilder.py`](file:///root/computer-user/case_brain/jack_the_ripper_casebuilder.py)

```bash
# 1. View Master Case Ledger & Statistics
python3 /root/computer-user/case_brain/jack_the_ripper_casebuilder.py ledger

# 2. Seed / Reconcile Case 1FDV-23-0001009 Ground Truth
python3 /root/computer-user/case_brain/jack_the_ripper_casebuilder.py seed

# 3. Generate Court-Ready Pleading Count
python3 /root/computer-user/case_brain/jack_the_ripper_casebuilder.py pleading --id <ALLEGATION_ID>

# 4. Generate Official Investigative Referral Memorandum
python3 /root/computer-user/case_brain/jack_the_ripper_casebuilder.py referral --id <ALLEGATION_ID>

# 5. Run Verification & Adversarial Kill Test Suite
python3 /root/computer-user/case_brain/jack_the_ripper_casebuilder.py test
```
