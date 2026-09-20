"""Live invoke of mega-skills runners when FDE_PATH_MEGA_SKILLS is set.

Default is --validate-only (safe). Full execute requires explicit opt-in.
Never runs network deploy / merge / push.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .estate import load_estate, resolve_repo

ALLOWED_PIPELINES = frozenset(
    {
        "inception-to-deployment",
        "control-plane",
        "memory-fleet",
        "change-swe",
        "ship-cloud",
        "cultivate-main",
        "anthropic-applied-ai-readiness",
    }
)


@dataclass
class InvokeResult:
    available: bool
    action: str
    status: str
    pipeline: str | None = None
    root: str | None = None
    returncode: int | None = None
    stdout_tail: str = ""
    stderr_tail: str = ""
    detail: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def mega_skills_root() -> Path | None:
    entry = resolve_repo(load_estate(), "mega_skills")
    if entry.get("available") and entry.get("effective_path"):
        return Path(entry["effective_path"])
    env = os.environ.get("FDE_PATH_MEGA_SKILLS")
    if env and Path(env).is_dir():
        return Path(env)
    return None


def _tail(text: str, n: int = 4000) -> str:
    if len(text) <= n:
        return text
    return text[-n:]


def invoke_pipeline(
    pipeline: str = "control-plane",
    *,
    validate_only: bool = True,
    timeout_sec: int = 120,
) -> InvokeResult:
    """Run mega-skills scripts/run_deep_work_pipeline.py against local checkout."""
    if pipeline not in ALLOWED_PIPELINES:
        return InvokeResult(
            available=False,
            action="reject",
            status="fail",
            pipeline=pipeline,
            detail={"error": f"pipeline not in allowlist: {sorted(ALLOWED_PIPELINES)}"},
        )

    root = mega_skills_root()
    if root is None:
        return InvokeResult(
            available=False,
            action="skip",
            status="skip",
            pipeline=pipeline,
            detail={
                "hint": "Set FDE_PATH_MEGA_SKILLS to local mega-skills checkout",
            },
        )

    runner = root / "scripts" / "run_deep_work_pipeline.py"
    if not runner.is_file():
        return InvokeResult(
            available=False,
            action="skip",
            status="fail",
            pipeline=pipeline,
            root=str(root),
            detail={"error": f"runner missing: {runner}"},
        )

    cmd = [
        sys.executable,
        str(runner),
        "--root",
        str(root),
        "--pipeline",
        pipeline,
    ]
    if validate_only:
        cmd.append("--validate-only")

    action = "validate_only" if validate_only else "execute_pipeline"
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return InvokeResult(
            available=True,
            action=action,
            status="timeout",
            pipeline=pipeline,
            root=str(root),
            detail={"error": str(exc), "timeout_sec": timeout_sec},
        )
    except OSError as exc:
        return InvokeResult(
            available=True,
            action=action,
            status="fail",
            pipeline=pipeline,
            root=str(root),
            detail={"error": str(exc)},
        )

    parsed: dict[str, Any] = {}
    out = proc.stdout or ""
    try:
        parsed = json.loads(out)
    except json.JSONDecodeError:
        parsed = {"raw": True}

    status = "ok" if proc.returncode == 0 else "fail"
    if isinstance(parsed, dict) and parsed.get("status"):
        # VALID / COMPLETE from runner
        if parsed["status"] in ("VALID", "COMPLETE") and proc.returncode == 0:
            status = "ok"

    return InvokeResult(
        available=True,
        action=action,
        status=status,
        pipeline=pipeline,
        root=str(root),
        returncode=proc.returncode,
        stdout_tail=_tail(out),
        stderr_tail=_tail(proc.stderr or ""),
        detail={"parsed": parsed, "cmd": cmd},
    )


def invoke_validate_hierarchy(timeout_sec: int = 180) -> InvokeResult:
    """Optional hierarchy validator when mega-skills is local."""
    root = mega_skills_root()
    if root is None:
        return InvokeResult(
            available=False,
            action="skip",
            status="skip",
            detail={"hint": "Set FDE_PATH_MEGA_SKILLS"},
        )
    script = root / "scripts" / "validate_hierarchy.py"
    if not script.is_file():
        return InvokeResult(
            available=False,
            action="skip",
            status="fail",
            root=str(root),
            detail={"error": "validate_hierarchy.py missing"},
        )
    try:
        proc = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return InvokeResult(
            available=True,
            action="validate_hierarchy",
            status="fail",
            root=str(root),
            detail={"error": str(exc)},
        )
    return InvokeResult(
        available=True,
        action="validate_hierarchy",
        status="ok" if proc.returncode == 0 else "fail",
        root=str(root),
        returncode=proc.returncode,
        stdout_tail=_tail(proc.stdout or ""),
        stderr_tail=_tail(proc.stderr or ""),
        detail={},
    )
