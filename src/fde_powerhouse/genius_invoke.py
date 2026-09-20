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


def _env_with_src(root: Path) -> dict[str, str]:
    env = os.environ.copy()
    src = root / "src"
    if src.is_dir():
        env["PYTHONPATH"] = str(src) + os.pathsep + env.get("PYTHONPATH", "")
    return env


def _tail(text: str, n: int = 4000) -> str:
    return text if len(text) <= n else text[-n:]


def invoke_genius_doctor(timeout_sec: int = 60) -> GeniusInvokeResult:
    root = genius_root()
    if root is None:
        return GeniusInvokeResult(
            available=False,
            action="skip",
            status="skip",
            detail={"hint": "Set FDE_PATH_GENIUS_MASTERY"},
        )
    env = _env_with_src(root)
    candidates = [
        [sys.executable, "-m", "genius", "--version"],
        [sys.executable, "-m", "genius", "doctor", "."],
    ]
    last_err = ""
    for cmd in candidates:
        try:
            proc = subprocess.run(
                cmd, cwd=str(root), capture_output=True, text=True,
                timeout=timeout_sec, env=env, check=False,
            )
        except (subprocess.TimeoutExpired, OSError) as exc:
            last_err = str(exc)
            continue
        if proc.returncode == 0:
            return GeniusInvokeResult(
                available=True, action=" ".join(cmd[2:]), status="ok",
                root=str(root), returncode=0,
                stdout_tail=_tail(proc.stdout or ""),
                stderr_tail=_tail(proc.stderr or ""),
                detail={"cmd": cmd},
            )
        last_err = _tail((proc.stderr or "") + (proc.stdout or ""))
    markers = {
        "GENIUS.yaml": (root / "GENIUS.yaml").is_file(),
        "ROLE.yaml": (root / "ROLE.yaml").is_file(),
        "pyproject.toml": (root / "pyproject.toml").is_file(),
    }
    if all(markers.values()):
        return GeniusInvokeResult(
            available=True, action="marker_probe", status="ok", root=str(root),
            detail={"markers": markers, "cli_note": last_err or "CLI soft; markers present"},
        )
    return GeniusInvokeResult(
        available=True, action="doctor", status="fail", root=str(root),
        detail={"error": last_err or "failed", "markers": markers},
    )


def invoke_genius_role_brief(
    role: str = "ForwardDeployedAgentic",
    outcomes: list[str] | None = None,
) -> GeniusInvokeResult:
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


def invoke_genius_synthesize(
    role: str = "ForwardDeployedAgentic",
    outcome: str = "field agentic delivery",
    dest: str | Path | None = None,
    timeout_sec: int = 180,
) -> GeniusInvokeResult:
    """Call `genius synthesize` when local Genius-Mastery is available."""
    root = genius_root()
    if root is None:
        return GeniusInvokeResult(
            available=False,
            action="synthesize",
            status="skip",
            detail={"hint": "Set FDE_PATH_GENIUS_MASTERY"},
        )
    dest_path = Path(dest) if dest else Path(".fde") / "genius_synth"
    dest_path.mkdir(parents=True, exist_ok=True)
    env = _env_with_src(root)
    cmd = [
        sys.executable, "-m", "genius", "synthesize", role,
        "--outcome", outcome,
        "--dest", str(dest_path.resolve()),
    ]
    mega = os.environ.get("FDE_PATH_MEGA_SKILLS")
    if mega and Path(mega).is_dir():
        cmd.extend(["--mega-skills-root", mega])
    try:
        proc = subprocess.run(
            cmd, cwd=str(root), capture_output=True, text=True,
            timeout=timeout_sec, env=env, check=False,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return GeniusInvokeResult(
            available=True, action="synthesize", status="fail", root=str(root),
            detail={"error": str(exc), "cmd": cmd},
        )
    return GeniusInvokeResult(
        available=True,
        action="synthesize",
        status="ok" if proc.returncode == 0 else "fail",
        root=str(root),
        returncode=proc.returncode,
        stdout_tail=_tail(proc.stdout or ""),
        stderr_tail=_tail(proc.stderr or ""),
        detail={"cmd": cmd, "dest": str(dest_path)},
    )
