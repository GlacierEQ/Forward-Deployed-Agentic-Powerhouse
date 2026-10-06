"""Thin fire-and-forget launcher for the Scale FDE workstream DAG.

This module does not replace Aspen/APEX/agent-coordinator runtimes. It owns only
mission-contract validation, dependency-frontier launch, bounded process dispatch,
resume-state validation, completion readback, and compact top-level receipts.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
from collections.abc import Callable, Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

import yaml

MISSION_SCHEMA = "glaciereq.scale-fde.mission.v1"
RESULT_SCHEMA = "glaciereq.scale-fde.orchestrator-result.v1"
DEFAULT_MAX_WORKERS = 4
SUCCESS_STATES = {
    "success",
    "succeeded",
    "ok",
    "complete",
    "completed",
    "pass",
    "passed",
}


class MissionOrchestrationError(ValueError):
    """Raised when a mission contract or continuation state is unsafe to launch."""


def _canonical_digest(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def mission_digest(mission: Mapping[str, Any]) -> str:
    """Hash the complete mission contract with mapping-order independence."""
    if not isinstance(mission, Mapping):
        raise MissionOrchestrationError("mission must be a mapping")
    return _canonical_digest(dict(mission))


def load_mission(path: str | Path) -> dict[str, Any]:
    """Load a YAML Scale mission contract."""
    source = Path(path)
    try:
        raw = yaml.safe_load(source.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise MissionOrchestrationError(f"mission file not found: {source}") from exc
    except yaml.YAMLError as exc:
        raise MissionOrchestrationError(f"invalid mission YAML: {exc}") from exc
    if not isinstance(raw, dict):
        raise MissionOrchestrationError("mission YAML must contain a mapping")
    return raw


def load_state(path: str | Path) -> dict[str, Any] | None:
    """Load a prior orchestrator checkpoint if it exists."""
    source = Path(path)
    if not source.exists():
        return None
    try:
        raw = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MissionOrchestrationError(
            f"invalid orchestrator state JSON: {exc}"
        ) from exc
    if not isinstance(raw, dict):
        raise MissionOrchestrationError("orchestrator state must contain a mapping")
    return raw


def write_state(path: str | Path, state: Mapping[str, Any]) -> Path:
    """Atomically persist an orchestrator checkpoint."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(dict(state), indent=2, sort_keys=True) + "\n"
    with NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=target.parent,
        prefix=f".{target.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        handle.write(rendered)
        temporary = Path(handle.name)
    os.replace(temporary, target)
    return target


def _completion_path(spec: Mapping[str, Any], raw_path: str) -> Path:
    artifact = Path(raw_path)
    if artifact.is_absolute():
        return artifact
    cwd = spec.get("cwd")
    return (Path(str(cwd)) / artifact) if cwd is not None else artifact


def _read_pointer(payload: Any, pointer: str) -> Any:
    current = payload
    for token in pointer.split("."):
        if not token:
            raise MissionOrchestrationError("completion pointer contains an empty token")
        if isinstance(current, Mapping):
            if token not in current:
                raise KeyError(token)
            current = current[token]
            continue
        if isinstance(current, Sequence) and not isinstance(
            current, (str, bytes, bytearray)
        ):
            try:
                current = current[int(token)]
            except (ValueError, IndexError) as exc:
                raise KeyError(token) from exc
            continue
        raise KeyError(token)
    return current


def _completion_check(spec: Mapping[str, Any]) -> dict[str, Any]:
    completion = spec.get("completion")
    if completion is None:
        return {"configured": False, "satisfied": True}
    if not isinstance(completion, Mapping):
        raise MissionOrchestrationError("completion must be a mapping")

    artifact_value = completion.get("artifact")
    pointer = completion.get("pointer")
    if not isinstance(artifact_value, str) or not artifact_value.strip():
        raise MissionOrchestrationError(
            "completion.artifact must be a non-empty string"
        )
    if not isinstance(pointer, str) or not pointer.strip():
        raise MissionOrchestrationError(
            "completion.pointer must be a non-empty dotted path"
        )
    expected = completion.get("equals", True)
    artifact = _completion_path(spec, artifact_value.strip())
    result: dict[str, Any] = {
        "configured": True,
        "artifact": str(artifact),
        "pointer": pointer,
        "expected": expected,
        "satisfied": False,
    }
    if not artifact.exists():
        result["reason"] = "artifact_missing"
        return result

    try:
        payload = json.loads(artifact.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        result["reason"] = "artifact_unreadable"
        result["error_type"] = type(exc).__name__
        return result

    try:
        observed = _read_pointer(payload, pointer)
    except KeyError:
        result["reason"] = "pointer_missing"
        return result

    result["observed"] = observed
    result["satisfied"] = observed == expected
    if not result["satisfied"]:
        result["reason"] = "value_mismatch"
    return result


def _normalize_workstreams(
    mission: Mapping[str, Any],
) -> tuple[dict[str, Any], ...]:
    schema = mission.get("schema")
    if schema != MISSION_SCHEMA:
        raise MissionOrchestrationError(
            f"mission schema must be {MISSION_SCHEMA!r}, got {schema!r}"
        )
    mission_id = mission.get("mission_id")
    if not isinstance(mission_id, str) or not mission_id.strip():
        raise MissionOrchestrationError("mission_id must be a non-empty string")

    raw = mission.get("workstreams")
    if not isinstance(raw, Sequence) or isinstance(
        raw, (str, bytes, bytearray)
    ):
        raise MissionOrchestrationError(
            "workstreams must be an ordered collection"
        )
    if not raw:
        raise MissionOrchestrationError("workstreams cannot be empty")

    normalized: list[dict[str, Any]] = []
    ids: list[str] = []
    for item in raw:
        if not isinstance(item, Mapping):
            raise MissionOrchestrationError("each workstream must be a mapping")
        workstream_id = item.get("id")
        if not isinstance(workstream_id, str) or not workstream_id.strip():
            raise MissionOrchestrationError(
                "workstream id must be a non-empty string"
            )
        workstream_id = workstream_id.strip()
        ids.append(workstream_id)

        deps = item.get("deps", [])
        if not isinstance(deps, Sequence) or isinstance(
            deps, (str, bytes, bytearray)
        ):
            raise MissionOrchestrationError(
                f"workstream {workstream_id!r} deps must be an ordered collection"
            )
        dep_ids = tuple(str(dep).strip() for dep in deps)
        if any(not dep for dep in dep_ids):
            raise MissionOrchestrationError(
                f"workstream {workstream_id!r} contains an empty dependency"
            )
        if len(set(dep_ids)) != len(dep_ids):
            raise MissionOrchestrationError(
                f"workstream {workstream_id!r} contains duplicate dependencies"
            )
        if workstream_id in dep_ids:
            raise MissionOrchestrationError(
                f"workstream {workstream_id!r} cannot depend on itself"
            )

        command = item.get("command")
        if not isinstance(command, Sequence) or isinstance(
            command, (str, bytes, bytearray)
        ):
            raise MissionOrchestrationError(
                f"workstream {workstream_id!r} command must be an argv collection"
            )
        argv = tuple(str(part) for part in command)
        if not argv or any(not part for part in argv):
            raise MissionOrchestrationError(
                f"workstream {workstream_id!r} command cannot be empty"
            )

        normalized_item = {
            **dict(item),
            "id": workstream_id,
            "deps": dep_ids,
            "command": argv,
        }
        # Validate the optional terminal readback contract at mission load time.
        if normalized_item.get("completion") is not None:
            _completion_check(normalized_item)
        normalized.append(normalized_item)

    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    if duplicates:
        raise MissionOrchestrationError(
            f"duplicate workstream ids: {duplicates}"
        )

    known = set(ids)
    for item in normalized:
        unknown = sorted(set(item["deps"]) - known)
        if unknown:
            raise MissionOrchestrationError(
                f"workstream {item['id']!r} has unknown dependency ids: {unknown}"
            )

    by_id = {item["id"]: item for item in normalized}
    state: dict[str, int] = {}

    def visit(workstream_id: str, path: list[str]) -> None:
        status = state.get(workstream_id, 0)
        if status == 2:
            return
        if status == 1:
            start = path.index(workstream_id)
            cycle = [*path[start:], workstream_id]
            raise MissionOrchestrationError(
                "dependency cycle: " + " -> ".join(cycle)
            )
        state[workstream_id] = 1
        path.append(workstream_id)
        for dep in by_id[workstream_id]["deps"]:
            visit(dep, path)
        path.pop()
        state[workstream_id] = 2

    for workstream_id in ids:
        visit(workstream_id, [])

    return tuple(normalized)


def _max_workers(mission: Mapping[str, Any], override: int | None) -> int:
    if override is not None:
        value = override
    else:
        orchestrator = mission.get("orchestrator") or {}
        if not isinstance(orchestrator, Mapping):
            raise MissionOrchestrationError("orchestrator must be a mapping")
        value = orchestrator.get("max_workers", DEFAULT_MAX_WORKERS)
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or not 1 <= value <= 64
    ):
        raise MissionOrchestrationError(
            "max_workers must be an integer in range 1..64"
        )
    return value


def _normalize_prior_state(
    workstreams: tuple[dict[str, Any], ...],
    digest: str,
    prior_state: Mapping[str, Any] | None,
) -> tuple[set[str], set[str], dict[str, Any], tuple[str, ...]]:
    if prior_state is None:
        return set(), set(), {}, ()
    if not isinstance(prior_state, Mapping):
        raise MissionOrchestrationError("prior_state must be a mapping")
    if prior_state.get("mission_digest") != digest:
        raise MissionOrchestrationError(
            "prior state mission digest does not match mission digest"
        )

    known = {item["id"] for item in workstreams}
    completed = set(prior_state.get("completed") or [])
    failed = set(prior_state.get("failed") or [])
    in_flight_raw = prior_state.get("in_flight") or []
    if isinstance(in_flight_raw, (str, bytes, bytearray)) or not isinstance(
        in_flight_raw, Sequence
    ):
        raise MissionOrchestrationError(
            "prior state in_flight must be an ordered collection"
        )
    in_flight = tuple(in_flight_raw)

    if not all(
        isinstance(item, str)
        for item in completed | failed | set(in_flight)
    ):
        raise MissionOrchestrationError(
            "prior state workstream ids must be strings"
        )
    unknown = sorted((completed | failed | set(in_flight)) - known)
    if unknown:
        raise MissionOrchestrationError(
            f"prior state contains unknown workstreams: {unknown}"
        )
    overlap = sorted(completed & failed)
    if overlap:
        raise MissionOrchestrationError(
            "prior state marks workstreams both completed and failed: "
            f"{overlap}"
        )

    by_id = {item["id"]: item for item in workstreams}
    for workstream_id in completed:
        missing = sorted(set(by_id[workstream_id]["deps"]) - completed)
        if missing:
            raise MissionOrchestrationError(
                f"prior completed workstream {workstream_id!r} "
                f"is not dependency-closed: {missing}"
            )

    receipts = prior_state.get("receipts") or {}
    if not isinstance(receipts, Mapping):
        raise MissionOrchestrationError(
            "prior state receipts must be a mapping"
        )
    return completed, failed, dict(receipts), in_flight


def _dispatch_success(receipt: Mapping[str, Any]) -> bool:
    completion = receipt.get("completion_check")
    if isinstance(completion, Mapping) and completion.get("configured"):
        return completion.get("satisfied") is True

    status = str(receipt.get("status") or "").casefold()
    returncode = receipt.get("returncode")
    if returncode is not None and returncode != 0:
        return False
    return status in SUCCESS_STATES


def _recover_completed_artifacts(
    order: Sequence[str],
    by_id: Mapping[str, Mapping[str, Any]],
    completed: set[str],
    failed: set[str],
    receipts: dict[str, Any],
    *,
    source: str,
) -> None:
    # Iterate because a recovered upstream artifact can unlock recovery of a
    # downstream artifact in the same preflight without dispatching anything.
    changed = True
    while changed:
        changed = False
        for workstream_id in order:
            if workstream_id in completed or workstream_id in failed:
                continue
            spec = by_id[workstream_id]
            if not all(dep in completed for dep in spec["deps"]):
                continue
            check = _completion_check(spec)
            if not check.get("configured") or not check.get("satisfied"):
                continue
            completed.add(workstream_id)
            receipts[workstream_id] = {
                "status": "success",
                "source": source,
                "completion_check": check,
            }
            changed = True


def run_mission(
    mission: Mapping[str, Any],
    *,
    dispatch: Callable[[dict[str, Any]], Mapping[str, Any]],
    prior_state: Mapping[str, Any] | None = None,
    max_workers: int | None = None,
    checkpoint: Callable[[Mapping[str, Any]], None] | None = None,
    retry_ambiguous: bool = False,
    retry_failed: bool = False,
) -> dict[str, Any]:
    """Launch each dependency-ready frontier and persist progress around each wave."""
    workstreams = _normalize_workstreams(mission)
    digest = mission_digest(mission)
    width = _max_workers(mission, max_workers)
    order = [item["id"] for item in workstreams]
    by_id = {item["id"]: item for item in workstreams}
    completed, failed, receipts, prior_in_flight = _normalize_prior_state(
        workstreams,
        digest,
        prior_state,
    )
    if retry_failed:
        for workstream_id in tuple(failed):
            receipts.pop(workstream_id, None)
        failed.clear()
    waves: list[list[str]] = []

    ambiguous_unresolved: list[str] = []
    for workstream_id in prior_in_flight:
        if workstream_id in completed or workstream_id in failed:
            continue
        check = _completion_check(by_id[workstream_id])
        if check.get("configured") and check.get("satisfied"):
            completed.add(workstream_id)
            receipts[workstream_id] = {
                "status": "success",
                "source": "ambiguous_readback_recovery",
                "completion_check": check,
            }
        elif retry_ambiguous:
            receipts.pop(workstream_id, None)
        else:
            ambiguous_unresolved.append(workstream_id)
    if ambiguous_unresolved:
        raise MissionOrchestrationError(
            "prior state contains ambiguous in-flight workstreams without "
            "terminal readback proof: "
            + ", ".join(ambiguous_unresolved)
        )

    _recover_completed_artifacts(
        order,
        by_id,
        completed,
        failed,
        receipts,
        source="completion_artifact_recovery",
    )

    def snapshot(
        status: str,
        blocked: Sequence[str] = (),
        in_flight: Sequence[str] = (),
    ) -> dict[str, Any]:
        blocked_set = set(blocked)
        return {
            "schema": RESULT_SCHEMA,
            "mission_id": mission["mission_id"],
            "mission_digest": digest,
            "status": status,
            "max_workers": width,
            "completed": [item for item in order if item in completed],
            "failed": [item for item in order if item in failed],
            "blocked": [item for item in order if item in blocked_set],
            "in_flight": [
                item for item in order if item in set(in_flight)
            ],
            "waves": [list(wave) for wave in waves],
            "receipts": {
                item: receipts[item]
                for item in order
                if item in receipts
            },
        }

    while True:
        pending = [
            item
            for item in order
            if item not in completed and item not in failed
        ]
        if not pending:
            result = snapshot(
                "COMPLETE" if not failed else "PARTIAL_FAILURE"
            )
            if checkpoint is not None:
                checkpoint(result)
            return result

        blocked_by_failure = [
            item
            for item in pending
            if any(dep in failed for dep in by_id[item]["deps"])
        ]
        ready = [
            item
            for item in pending
            if item not in blocked_by_failure
            and all(dep in completed for dep in by_id[item]["deps"])
        ]

        if not ready:
            blocked = [
                item
                for item in pending
                if item in blocked_by_failure
                or any(
                    dep not in completed
                    for dep in by_id[item]["deps"]
                )
            ]
            result = snapshot("BLOCKED", blocked)
            if checkpoint is not None:
                checkpoint(result)
            return result

        wave = list(ready)
        waves.append(wave)
        if checkpoint is not None:
            checkpoint(snapshot("RUNNING", in_flight=wave))

        outcomes: dict[str, Mapping[str, Any]] = {}
        with ThreadPoolExecutor(
            max_workers=min(width, len(wave))
        ) as pool:
            futures = {
                pool.submit(
                    dispatch,
                    dict(by_id[workstream_id]),
                ): workstream_id
                for workstream_id in wave
            }
            for future in as_completed(futures):
                workstream_id = futures[future]
                try:
                    receipt = future.result()
                    if not isinstance(receipt, Mapping):
                        raise TypeError(
                            "dispatch receipt must be a mapping"
                        )
                    outcomes[workstream_id] = dict(receipt)
                except Exception as exc:
                    outcomes[workstream_id] = {
                        "status": "failed",
                        "error_type": type(exc).__name__,
                        "error": str(exc),
                    }

        for workstream_id in wave:
            receipt = dict(outcomes[workstream_id])
            receipts[workstream_id] = receipt
            if _dispatch_success(receipt):
                completed.add(workstream_id)
            else:
                failed.add(workstream_id)

        if checkpoint is not None:
            pending_after = [
                item
                for item in order
                if item not in completed and item not in failed
            ]
            blocked_after = [
                item
                for item in pending_after
                if any(dep in failed for dep in by_id[item]["deps"])
            ]
            checkpoint(
                snapshot(
                    "RUNNING",
                    blocked_after,
                    in_flight=(),
                )
            )


def _digest_text(value: str) -> str:
    return "sha256:" + hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def subprocess_dispatch(spec: Mapping[str, Any]) -> dict[str, Any]:
    """Execute one explicit argv command without a shell and read back completion."""
    command = spec.get("command")
    if not isinstance(command, Sequence) or isinstance(
        command, (str, bytes, bytearray)
    ):
        raise MissionOrchestrationError(
            "command must be an argv collection"
        )
    argv = [str(part) for part in command]
    if not argv or any(not part for part in argv):
        raise MissionOrchestrationError("command cannot be empty")

    cwd = spec.get("cwd")
    if cwd is not None:
        cwd = str(cwd)
    timeout = spec.get("timeout_seconds", 3600)
    if (
        isinstance(timeout, bool)
        or not isinstance(timeout, (int, float))
        or timeout <= 0
    ):
        raise MissionOrchestrationError(
            "timeout_seconds must be positive"
        )

    env = None
    extra_env = spec.get("env")
    if extra_env is not None:
        if not isinstance(extra_env, Mapping) or not all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in extra_env.items()
        ):
            raise MissionOrchestrationError(
                "env must be a string-to-string mapping"
            )
        env = os.environ.copy()
        env.update(extra_env)

    started = time.perf_counter()
    try:
        process = subprocess.run(
            argv,
            cwd=cwd,
            env=env,
            timeout=float(timeout),
            capture_output=True,
            text=True,
            shell=False,
            check=False,
        )
        elapsed_ms = round(
            (time.perf_counter() - started) * 1000,
            3,
        )
        stdout = process.stdout or ""
        stderr = process.stderr or ""
        completion_check = _completion_check(spec)
        transport_success = process.returncode == 0
        status = (
            "success"
            if (
                completion_check.get("satisfied")
                if completion_check.get("configured")
                else transport_success
            )
            else "failed"
        )
        return {
            "status": status,
            "transport_status": (
                "success" if transport_success else "failed"
            ),
            "returncode": process.returncode,
            "elapsed_ms": elapsed_ms,
            "command_sha256": _canonical_digest({"argv": argv}),
            "stdout_sha256": _digest_text(stdout),
            "stderr_sha256": _digest_text(stderr),
            "stdout_preview": stdout[:2000],
            "stderr_preview": stderr[:2000],
            "completion_check": completion_check,
            "shell": False,
        }
    except subprocess.TimeoutExpired as exc:
        elapsed_ms = round(
            (time.perf_counter() - started) * 1000,
            3,
        )
        stdout = (
            exc.stdout.decode()
            if isinstance(exc.stdout, bytes)
            else (exc.stdout or "")
        )
        stderr = (
            exc.stderr.decode()
            if isinstance(exc.stderr, bytes)
            else (exc.stderr or "")
        )
        return {
            "status": "failed",
            "transport_status": "timeout",
            "error_type": "TimeoutExpired",
            "elapsed_ms": elapsed_ms,
            "command_sha256": _canonical_digest({"argv": argv}),
            "stdout_sha256": _digest_text(stdout),
            "stderr_sha256": _digest_text(stderr),
            "stdout_preview": stdout[:2000],
            "stderr_preview": stderr[:2000],
            "completion_check": _completion_check(spec),
            "shell": False,
        }
