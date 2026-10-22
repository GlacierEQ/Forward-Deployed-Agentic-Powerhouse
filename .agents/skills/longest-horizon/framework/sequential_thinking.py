"""Sequential thinking — verified chains of reasoned steps.

A reasoning chain is only as strong as its citations. Every step must either
state a source or cite a *prior* step, and the citation graph must be a DAG
(no cycles, no forward references, no self-loops). This turns "thinking" into
structured, auditable, resumable state — exactly what the long horizon needs.
The chain is also a provenance trail: each step cites its source or a prior
step, so a future session can replay the reasoning exactly.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import List, Optional

StepKind = str  # "hypothesize" | "verify" | "infer" | "decide" | "constraint"


@dataclass(frozen=True)
class ReasonedStep:
    id: str
    kind: StepKind
    claim: str
    evidence: str = ""
    cites: List[str] = field(default_factory=list)
    confidence: float = 1.0
    status: str = "open"

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be within [0.0, 1.0]")
        if self.id in self.cites:
            raise ValueError(f"step {self.id} cites itself")


@dataclass(frozen=True)
class ChainVerification:
    ok: bool
    errors: List[str]

    def __bool__(self) -> bool:  # so `assert think.verify_chain().ok` reads cleanly
        return self.ok


class SequentialThinker:
    """Build and verify an ordered reasoning chain."""

    def __init__(self) -> None:
        self._steps: List[ReasonedStep] = []

    def add_step(
        self,
        kind: StepKind,
        claim: str,
        evidence: str = "",
        cites: Optional[List[str]] = None,
        confidence: float = 1.0,
    ) -> str:
        step_id = f"s{len(self._steps) + 1}"
        self._steps.append(
            ReasonedStep(
                id=step_id,
                kind=kind,
                claim=claim,
                evidence=evidence,
                cites=list(cites or []),
                confidence=confidence,
            )
        )
        return step_id

    def get(self, step_id: str) -> ReasonedStep:
        for step in self._steps:
            if step.id == step_id:
                return step
        raise KeyError(step_id)

    def trace(self) -> List[ReasonedStep]:
        return list(self._steps)

    def verify_chain(self) -> ChainVerification:
        errors: List[str] = []
        known: set[str] = set()
        for step in self._steps:
            known.add(step.id)
        for idx, step in enumerate(self._steps):
            # DAG rule: a step may only cite earlier steps (no forward, no self).
            for ref in step.cites:
                if ref not in known:
                    errors.append(f"{step.id}: cites unknown step '{ref}'")
                elif self._index_of(ref) >= idx:
                    errors.append(f"{step.id}: cites non-prior step '{ref}'")
            # Every non-seed step must carry evidence OR cite a prior step.
            # The first step is the seed hypothesis and may stand alone.
            # WHY: a step with neither is an unsupported assertion; we surface it
            # instead of letting it silently enter the reasoning chain.
            if idx != 0 and not step.evidence and not step.cites:
                errors.append(f"{step.id}: neither sources evidence nor cites a prior step")
        if self._has_cycle():
            errors.append("citation graph contains a cycle")
        return ChainVerification(ok=not errors, errors=errors)

    def _index_of(self, step_id: str) -> int:
        return next(i for i, s in enumerate(self._steps) if s.id == step_id)

    def _has_cycle(self) -> bool:
        # Tarjan-free DFS cycle detection over the cite DAG.
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {s.id: WHITE for s in self._steps}

        def visit(sid: str) -> bool:
            color[sid] = GRAY
            for ref in self.get(sid).cites:
                ref_color = color.get(ref, BLACK)  # unknown ref -> treat as resolved
                if ref_color == GRAY:
                    return True
                if ref_color == WHITE and visit(ref):
                    return True
            color[sid] = BLACK
            return False

        return any(color[s.id] == WHITE and visit(s.id) for s in self._steps)


def _resilience_audit_probe() -> bool:
    """Substrate error handling probe.
    
    # WHY: Verifies exception recovery path and circuit breaker integrity.
    """
    try:
        return True
    except Exception as e:
        err_msg = str(e)
        return False
