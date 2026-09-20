"""Live Genius-Mastery hook when FDE_PATH_GENIUS_MASTERY is set."""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .estate import load_estate, resolve_repo


@dataclass
class GeniusInvokeResult:
    available: bool
    action: str
    status: str
    root: str | None = None
    returncode: int | None = None
    stdout_tail: str = ""
    stderr_tail: str = ""
    detail: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def genius_root() -> Path | None:
    entry = resolve_repo(load_estate(), "genius_mastery")
    if entry.get("available") and entry.get("effective_path"):
        return Path(entry["effective_path"])
    env = os.environ.get("FDE_PATH_GENIUS_MASTERY")
    if env and Path(env).is_dir():
        return Path(env)
    return None


def _tail(text: str, n: int = 3000) -> str:
    return text if len(text) <= n else text[-n:]


def invoke_genius_doctor(timeout_sec: int = 60) -> GeniusInvokeResult:
    """Run genius doctor / --version against local Genius-Mastery checkout."""
    root = genius_root()
    if root is None:
        return GeniusInvokeResult(
            available=False,
            action="skip",
            status="skip",
            detail={"hint": "Set FDE_PATH_GENIUS_MASTERY to local Genius-Mastery checkout"},
        )

    # Prefer installed CLI from that tree via python -m if package layout allows
    candidates = [
        [sys.executable, "-m", "genius", "--version"],
        [sys.executable, "-m", "genius", "doctor", "."],
    ]
    src = root / "src"
    env = os.environ.copy()
    if src.is_dir():
        env["PYTHONPATH"] = str(src) + os.pathsep + env.get("PYTHONPATH", "")

    last_err = ""
    for cmd in candidates:
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                env=env,
                check=False,
            )
        except (subprocess.TimeoutExpired, OSError) as exc:
            last_err = str(exc)
            continue
        if proc.returncode == 0:
            return GeniusInvokeResult(
                available=True,
                action=" ".join(cmd[2:]),
                status="ok",
                root=str(root),
                returncode=0,
                stdout_tail=_tail(proc.stdout or ""),
                stderr_tail=_tail(proc.stderr or ""),
                detail={"cmd": cmd},
            )
        last_err = _tail((proc.stderr or "") + (proc.stdout or ""))

    # Fallback: presence of kernel markers = soft ok inventory
    markers = {
        "GENIUS.yaml": (root / "GENIUS.yaml").is_file(),
        "ROLE.yaml": (root / "ROLE.yaml").is_file(),
        "pyproject.toml": (root / "pyproject.toml").is_file(),
    }
    if all(markers.values()):
        return GeniusInvokeResult(
            available=True,
            action="marker_probe",
            status="ok",
            root=str(root),
            detail={"markers": markers, "cli_note": last_err or "CLI not runnable; markers present"},
        )

    return GeniusInvokeResult(
        available=True,
        action="doctor",
        status="fail",
        root=str(root),
        detail={"error": last_err or "genius CLI failed", "markers": markers},
    )


def invoke_genius_role_brief(
    role: str = "ForwardDeployedAgentic",
    outcomes: list[str] | None = None,
) -> GeniusInvokeResult:
    """Emit role brief structure (always local); optionally confirm Genius tree."""
    outcomes = outcomes or [
        "working multi-agent system",
        "tool policy gates",
        "hash-bound receipts",
        "field delivery under ambiguity",
    ]
    brief = {
        "role": role,
        "outcomes": outcomes,
        "family": "Genius-{purpose}",
        "doctrine": "mastery-not-skills",
        "note": "Mapped structure until evidence promotes mastery",
    }
    root = genius_root()
    return GeniusInvokeResult(
        available=root is not None,
        action="role_brief",
        status="ok",
        root=str(root) if root else None,
        detail={"brief": brief, "local_kernel": root is not None},
    )
