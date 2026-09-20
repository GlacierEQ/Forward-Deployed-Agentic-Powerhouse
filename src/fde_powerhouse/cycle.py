"""Full-cycle runner — zero to hero for every mode."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .modes import MODES, mode_emphasis
from .receipts import CycleReceipt, StageReceipt
from .stages import STAGE_FNS


def run_cycle(
    mode: str,
    target: str = "default",
    work_dir: str | Path = ".",
    stop_on_fail: bool = True,
    problem: str = "",
) -> CycleReceipt:
    if mode not in MODES:
        raise ValueError(f"Unknown mode {mode!r}; choose from {MODES}")

    ctx: dict[str, Any] = {"work_dir": str(work_dir), "problem": problem}
    stages: list[StageReceipt] = []
    overall = "ok"

    for stage_name in mode_emphasis(mode):
        fn = STAGE_FNS.get(stage_name)
        if fn is None:
            receipt = StageReceipt(
                stage=stage_name,
                mode=mode,
                status="skip",
                summary=f"No adapter for stage {stage_name}",
            )
        else:
            receipt = fn(mode, target, ctx)
        stages.append(receipt)
        if receipt.status == "fail":
            overall = "fail"
            if stop_on_fail:
                break

    return CycleReceipt(mode=mode, target=target, stages=stages, status=overall)
