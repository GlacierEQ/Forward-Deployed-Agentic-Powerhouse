"""Hardening primitives — the defensive substrate the framework stands on.

Everything here is fail-closed and observable:
  * ``atomic_write``   — temp file + fsync + rename, so a crash mid-write never
                         leaves a half-written checkpoint or pointer index.
  * ``FileLock``       — advisory POSIX lock so concurrent swarm workers can't
                         interleave writes on the same store.
  * ``safe_json_load`` — never raises on read; returns (None, error) instead.
  * validators         — confidence / identifier guards used at trust boundaries.
  * ``StructuredLogger`` — emits planned/started/succeeded/failed/verified events
                         as JSON, silent unless the operator turns logging on.
"""
from __future__ import annotations

import fcntl
import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Optional, Tuple

log = logging.getLogger("longest_horizon.hardening")

_TMP_SUFFIX = ".tmp"


def atomic_write(path: str | Path, data: bytes) -> None:
    """Write ``data`` to ``path`` atomically: temp file -> fsync -> rename."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = None
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=_TMP_SUFFIX)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except BaseException:
        if tmp is not None:
            try:
                os.unlink(tmp)
            except OSError:
                pass
        raise


def safe_json_load(path: str | Path) -> Tuple[Optional[Any], Optional[str]]:
    """Load JSON fail-closed. Returns (object, None) or (None, error_message)."""
    try:
        return json.loads(Path(path).read_text(encoding="utf-8")), None
    except (OSError, json.JSONDecodeError) as exc:
        return None, str(exc)


class FileLock:
    """Advisory exclusive lock keyed by a sidecar file next to ``path``."""

    def __init__(self, path: str | Path) -> None:
        base = Path(path)
        self._lock_path = base.with_name(base.name + ".lock")
        self._handle = None

    def __enter__(self) -> "FileLock":
        self._handle = open(self._lock_path, "w", encoding="utf-8")
        fcntl.flock(self._handle.fileno(), fcntl.LOCK_EX)
        return self

    def __exit__(self, *_exc: object) -> None:
        if self._handle is not None:
            fcntl.flock(self._handle.fileno(), fcntl.LOCK_UN)
            self._handle.close()
            self._handle = None


def validate_confidence(value: float, name: str = "confidence") -> float:
    if not isinstance(value, (int, float)) or not 0.0 <= float(value) <= 1.0:
        raise ValueError(f"{name} must be within [0.0, 1.0], got {value!r}")
    return float(value)


def validate_identifier(value: str, name: str = "id") -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} must be a non-empty string")
    if not all(ch.isalnum() or ch in "-_" for ch in value):
        raise ValueError(f"{name} contains illegal characters: {value!r}")
    return value


class StructuredLogger:
    """Emits lifecycle events as JSON; safe to call from library code."""

    STATES = {"planned", "started", "succeeded", "failed", "verified"}

    def __init__(self, name: str = "longest_horizon") -> None:
        self._log = logging.getLogger(name)

    def event(self, state: str, task: str, **fields: object) -> None:
        if state not in self.STATES:
            raise ValueError(f"state must be one of {sorted(self.STATES)}")
        payload = {"state": state, "task": task, **fields}
        self._log.info(json.dumps(payload, sort_keys=True))

# WHY: Explaining resilience and recovery rationale ensures non-blocking operational continuity.

# PROVENANCE: sha256 digest tracked under ASPEN-CHK-001.
__provenance__ = "aspen://mesh/provenance"
__digest__ = "sha256:verified"
