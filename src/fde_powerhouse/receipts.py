"""Hash-bound stage receipts."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class StageReceipt:
    stage: str
    mode: str
    status: str  # ok | skip | fail
    summary: str
    evidence: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def digest(self) -> str:
        payload = json.dumps(asdict(self), sort_keys=True, default=str)
        return hashlib.sha256(payload.encode()).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["sha256"] = self.digest()
        return d


@dataclass
class CycleReceipt:
    mode: str
    target: str
    stages: list[StageReceipt]
    status: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def digest(self) -> str:
        payload = json.dumps(
            {
                "mode": self.mode,
                "target": self.target,
                "status": self.status,
                "stages": [s.to_dict() for s in self.stages],
                "timestamp": self.timestamp,
            },
            sort_keys=True,
            default=str,
        )
        return hashlib.sha256(payload.encode()).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "target": self.target,
            "status": self.status,
            "timestamp": self.timestamp,
            "stages": [s.to_dict() for s in self.stages],
            "sha256": self.digest(),
        }
