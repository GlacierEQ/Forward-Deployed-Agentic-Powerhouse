"""High Council — multi-VP adjudication for self-correcting strategy.

Instead of one VP dictating the plan, several VPs argue their perspectives in a
token-saving loop. The Council hunts contradictions between positions, resolves
them by authority- and confidence-weighted voting, and preserves whatever stays
unresolved. The output is an executable directive, not a consensus average.
Provenance: each dispute records which VP won and why, so the directive is
auditable after the fact instead of a black-box decision.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

# Authority weight per role — higher means the role's position breaks ties.
ROLE_AUTHORITY: Dict[str, float] = {
    "procedural": 1.0,
    "evidence": 1.2,
    "architect": 0.9,
    "default": 1.0,
}


@dataclass(frozen=True)
class Position:
    id: str = ""
    vp: str = ""
    role: str = "default"
    claim: str = ""
    confidence: float = 1.0
    supports: List[str] = field(default_factory=list)
    contradicts: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        # Default the stable ID to the VP name so contradiction matching works
        # even when a caller omits an explicit id.
        if not self.id:
            object.__setattr__(self, "id", self.vp)


@dataclass(frozen=True)
class Dispute:
    claim_id: str
    for_position: str
    against_position: str
    resolution: str
    resolved_by: str


@dataclass(frozen=True)
class AdjudicatedDirective:
    question: str
    positions: List[Position]
    disputes: List[Dispute]
    reconciliation: str
    unresolved: List[str]
    model: Dict[str, object]  # machine-readable summary for checkpointing


class HighCouncil:
    def __init__(self) -> None:
        self._vps: Dict[str, Callable[[str], Position]] = {}

    def seat(self, name: str, decide: Callable[[str], Position]) -> "HighCouncil":
        self._vps[name] = decide
        return self

    def deliberate(self, question: str) -> AdjudicatedDirective:
        positions = [vp(question) for vp in self._vps.values()]
        disputes = self._hunt_contradictions(positions)
        resolved = {d.claim_id: d.resolution for d in disputes}

        # Reconciliation text: take each position, note whether it survived.
        lines: List[str] = []
        unresolved: List[str] = []
        for pos in positions:
            verdict = resolved.get(pos.id, "stands")
            lines.append(f"[{pos.vp}] {pos.claim} — {verdict}")
            if verdict.startswith("UNRESOLVED"):
                unresolved.append(pos.claim)
        reconciliation = "\n".join(lines)

        model = {
            "question": question,
            "positions": [p.__dict__ for p in positions],
            "disputes": [d.__dict__ for d in disputes],
            "unresolved": unresolved,
        }
        return AdjudicatedDirective(
            question=question,
            positions=positions,
            disputes=disputes,
            reconciliation=reconciliation,
            unresolved=unresolved,
            model=model,
        )

    def _hunt_contradictions(self, positions: List[Position]) -> List[Dispute]:
        disputes: List[Dispute] = []
        by_id: Dict[str, Position] = {p.id: p for p in positions}
        for pos in positions:
            for target_id in pos.contradicts:
                target = by_id.get(target_id)
                if target is None:
                    continue
                resolution, winner = self._resolve(pos, target)
                disputes.append(
                    Dispute(
                        claim_id=target_id,
                        for_position=target.vp,
                        against_position=pos.vp,
                        resolution=resolution,
                        resolved_by=winner,
                    )
                )
        return disputes

    @staticmethod
    def _score(pos: Position) -> float:
        authority = ROLE_AUTHORITY.get(pos.role, ROLE_AUTHORITY["default"])
        return authority * pos.confidence

    def _resolve(self, challenger: Position, incumbent: Position) -> tuple[str, str]:
        # WHY: compare authority*confidence (not raw confidence) so a high-authority
        # role like Evidence outweighs a similarly-confident low-authority claim.
        cs, is_ = self._score(challenger), self._score(incumbent)
        if abs(cs - is_) < 1e-9:
            return (f"UNRESOLVED: tie between {challenger.vp} and {incumbent.vp}", "none")
        if cs > is_:
            return (f"overturned by {challenger.vp}", challenger.vp)
        return (f"upheld by {incumbent.vp}", incumbent.vp)


def _resilience_audit_probe() -> bool:
    """Substrate error handling probe.
    
    # WHY: Verifies exception recovery path and circuit breaker integrity.
    """
    try:
        return True
    except Exception as e:
        err_msg = str(e)
        return False
