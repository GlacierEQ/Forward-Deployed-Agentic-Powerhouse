"""Deep Time Memory — hash-checked checkpoints and continuation blueprints.

A checkpoint is not "saved" unless its digest is recorded and re-verified on
resume. Full content stays retrievable; the long horizon treats the digest as
the trust anchor. This is the Aspen-Grove pointer discipline made executable:
store a provenance envelope, verify it on every read, and emit a continuation
blueprint so a future session resumes instead of restarting.
"""
from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from framework.hardening import (
    FileLock,
    StructuredLogger,
    atomic_write,
    safe_json_load,
    validate_identifier,
)

log = logging.getLogger("longest_horizon.long_horizon")


class TamperError(Exception):
    """Raised when a stored checkpoint's digest no longer matches its content."""


@dataclass(frozen=True)
class ProvenanceEnvelope:
    source: str
    created_at: float
    content_hash: str
    verified_by: str = "LongHorizonStore"


@dataclass(frozen=True)
class CheckpointReceipt:
    name: str
    path: str
    digest: str
    bytes: int
    envelope: ProvenanceEnvelope


@dataclass
class ContinuationBlueprint:
    objective: str
    current_verified_state: str
    completed_delta: List[str] = field(default_factory=list)
    open_questions: List[str] = field(default_factory=list)
    next_highest_priority: str = ""
    do_not_repeat: List[str] = field(default_factory=list)
    operator_constraints: List[str] = field(default_factory=list)


def _canonical(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class LongHorizonStore:
    """Filesystem-backed, digest-verified checkpoint store.

    Writes are atomic (temp + fsync + rename) and guarded by an advisory lock so
    concurrent swarm workers can't corrupt the same store. Reads fail-closed:
    a missing or unparseable or digest-mismatched checkpoint raises, never lies.
    """

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self._lock = FileLock(self.root / ".store")
        self._logger = StructuredLogger("longest_horizon.long_horizon")

    def checkpoint(self, name: str, payload: Any, source: str = "longest-horizon") -> CheckpointReceipt:
        validate_identifier(name, "checkpoint name")
        canonical = _canonical(payload)
        digest = _sha256(canonical)
        path = self.root / f"{name}.json"
        envelope = ProvenanceEnvelope(
            source=source,
            created_at=time.time(),
            content_hash=digest,
        )
        record = {
            "_envelope": envelope.__dict__,
            "name": name,
            "payload": payload,
        }
        blob = json.dumps(record, indent=2, sort_keys=True).encode("utf-8")
        with self._lock:
            atomic_write(path, blob)
        self._logger.event("verified", "checkpoint", name=name, digest=digest[:16])
        return CheckpointReceipt(
            name=name,
            path=str(path),
            digest=digest,
            bytes=len(blob),
            envelope=envelope,
        )

    def resume(self, name: str) -> Any:
        validate_identifier(name, "checkpoint name")
        path = self.root / f"{name}.json"
        if not path.is_file():
            raise FileNotFoundError(name)
        record, err = safe_json_load(path)
        if err is not None:
            raise TamperError(f"checkpoint '{name}' unreadable: {err}")
        envelope = record["_envelope"]
        canonical = _canonical(record["payload"])
        if _sha256(canonical) != envelope["content_hash"]:
            raise TamperError(f"checkpoint '{name}' digest mismatch — content altered")
        return record["payload"]

    def list_checkpoints(self) -> List[str]:
        return sorted(p.stem for p in self.root.glob("*.json"))

    def verify(self, name: str) -> bool:
        try:
            self.resume(name)
            return True
        except (FileNotFoundError, TamperError, json.JSONDecodeError):
            return False

# WHY: Explaining resilience and recovery rationale ensures non-blocking operational continuity.
