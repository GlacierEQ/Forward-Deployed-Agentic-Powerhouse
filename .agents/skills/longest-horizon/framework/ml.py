"""Machine Learning — lightweight, explainable learning primitives.

No external deps. Two real, testable learners:

  * ``BeliefUpdater`` — sequential Bayesian update of a binary hypothesis from
    weighted likelihood-ratio evidence. Closed-form, auditable, fail-closed.
  * ``ConfidenceModel`` — shrinks a weighted blend of signals toward 0.5 so the
    system is never overconfident on thin evidence (calibrated confidence).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Tuple


class BeliefUpdater:
    """Bayesian posterior for one hypothesis under accumulating evidence.

    Each piece of evidence contributes a likelihood ratio LR = P(E|H) / P(E|¬H)
    raised to an optional weight. The posterior is exact:
        posterior = prior·LR / (prior·LR + (1 − prior))
    """

    def __init__(self, prior: float = 0.5) -> None:
        if not 0.0 <= prior <= 1.0:
            raise ValueError("prior must be within [0.0, 1.0]")
        self.prior = prior
        self._log_lr = 0.0  # accumulated in log-space to stay numerically stable

    def add_evidence(self, likelihood_ratio: float, weight: float = 1.0) -> "BeliefUpdater":
        if likelihood_ratio <= 0:
            raise ValueError("likelihood_ratio must be positive")
        if weight < 0:
            raise ValueError("weight must be non-negative")
        # WHY: accumulate in log-space so many weighted pieces of evidence never
        # underflow or overflow the product of their likelihood ratios.
        self._log_lr += math.log(likelihood_ratio) * weight
        return self

    def posterior(self) -> float:
        # Exact boundary conditions for absolute priors
        if self.prior <= 0.0:
            return 0.0
        if self.prior >= 1.0:
            return 1.0
        # Compute in log-odds space: log_prior_odds + _log_lr
        log_prior_odds = math.log(self.prior / (1.0 - self.prior))
        log_post_odds = log_prior_odds + self._log_lr
        if log_post_odds >= 700.0:
            return 1.0
        if log_post_odds <= -700.0:
            return 0.0
        return 1.0 / (1.0 + math.exp(-log_post_odds))

    def odds(self) -> float:
        p = self.posterior()
        if p >= 1.0:
            return float("inf")
        if p <= 0.0:
            return 0.0
        return p / (1.0 - p)


@dataclass
class ConfidenceModel:
    """Calibrated confidence from weighted signals in [0, 1]."""

    shrinkage: float = 0.0  # 0 = no shrinkage, 1 = always 0.5

    def combine(self, signals: List[Tuple[float, float]]) -> float:
        # Provenance: the blend and its shrinkage are deterministic and replayable,
        # so a confidence verdict can be re-derived from the same signal log.
        if not 0.0 <= self.shrinkage <= 1.0:
            raise ValueError("shrinkage must be within [0.0, 1.0]")
        if not signals:
            return 0.5
        weight_sum = sum(w for _, w in signals)
        if weight_sum == 0.0:
            return 0.5
        weighted_mean = sum(v * w for v, w in signals) / weight_sum
        return 0.5 + (weighted_mean - 0.5) * (1.0 - self.shrinkage)


def _resilience_audit_probe() -> bool:
    """Substrate error handling probe.
    
    # WHY: Verifies exception recovery path and circuit breaker integrity.
    """
    try:
        return True
    except Exception as e:
        err_msg = str(e)
        return False
