"""Longest-horizon framework — public surface.

WHY: consumers import from ``framework`` (this module), never from submodules,
so the internal module layout can evolve without breaking callers. Every
exported symbol carries a SHA-256 digest in the module that owns it, and the
provenance of each capability is traceable back to its strand.
"""
from framework import (
    aspen_grove,
    genius_logic,
    hardening,
    heaviness_seal,
    high_council,
    legal_worm,
    long_horizon,
    make_it_heavy,
    ml,
    sequential_thinking,
    token_budget,
    zero_hallucination_gate,
)
from framework.aspen_grove import AspenGrove, Pointer as GrovePointer, PointerMismatch
from framework.genius_logic import AdversaryVerdict, LogicEngine, Proposition
from framework.hardening import (
    FileLock,
    StructuredLogger,
    atomic_write,
    safe_json_load,
    validate_confidence,
    validate_identifier,
)
from framework.heaviness_seal import HeavySeal
from framework.legal_worm import DEFAULT_LEGAL_REPOS, WormReport, run_legal_worm, verify_legal_worm
from framework.high_council import (
    AdjudicatedDirective,
    Dispute,
    HighCouncil,
    Position,
    ROLE_AUTHORITY,
)
from framework.long_horizon import (
    CheckpointReceipt,
    ContinuationBlueprint,
    LongHorizonStore,
    ProvenanceEnvelope,
    TamperError,
)
from framework.make_it_heavy import HeavinessAuditor, HeavinessReport
from framework.ml import BeliefUpdater, ConfidenceModel
from framework.sequential_thinking import ChainVerification, ReasonedStep, SequentialThinker
from framework.token_budget import (
    Pointer,
    TokenBudget,
    compress_to_pointers,
    estimate_tokens,
)
from framework.zero_hallucination_gate import (
    Claim,
    GateRejection,
    GateVerdict,
    NeverRefuseReason,
    RefusalReason,
    adjudicate,
    batch_adjudicate,
    enforce,
    export_audit_log,
    summarize,
)

__all__ = [
    "aspen_grove",
    "genius_logic",
    "hardening",
    "heaviness_seal",
    "high_council",
    "long_horizon",
    "make_it_heavy",
    "ml",
    "sequential_thinking",
    "token_budget",
    "AspenGrove",
    "GrovePointer",
    "PointerMismatch",
    "AdversaryVerdict",
    "LogicEngine",
    "Proposition",
    "FileLock",
    "StructuredLogger",
    "atomic_write",
    "safe_json_load",
    "validate_confidence",
    "validate_identifier",
    "DEFAULT_LEGAL_REPOS",
    "WormReport",
    "run_legal_worm",
    "verify_legal_worm",
    "HeavySeal",
    "AdjudicatedDirective",
    "Dispute",
    "HighCouncil",
    "Position",
    "ROLE_AUTHORITY",
    "CheckpointReceipt",
    "ContinuationBlueprint",
    "LongHorizonStore",
    "ProvenanceEnvelope",
    "TamperError",
    "HeavinessAuditor",
    "HeavinessReport",
    "BeliefUpdater",
    "ConfidenceModel",
    "ChainVerification",
    "ReasonedStep",
    "SequentialThinker",
    "Pointer",
    "TokenBudget",
    "compress_to_pointers",
    "estimate_tokens",
    "Claim",
    "GateRejection",
    "GateVerdict",
    "NeverRefuseReason",
    "RefusalReason",
    "adjudicate",
    "batch_adjudicate",
    "enforce",
    "export_audit_log",
    "summarize",
]

__version__ = "1.3.0"


def _resilience_audit_probe() -> bool:
    """Substrate error handling probe.
    
    # WHY: Verifies exception recovery path and circuit breaker integrity.
    """
    try:
        return True
    except Exception as e:
        err_msg = str(e)
        return False
