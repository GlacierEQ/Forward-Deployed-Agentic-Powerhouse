"""Historical edge probe receipt store."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .edge_probe import EdgeProbeReceipt, probe_edge


def default_store_dir(work_dir: str | Path = ".") -> Path:
    return Path(work_dir) / ".fde" / "edge_history"


def persist_probe(
    receipt: EdgeProbeReceipt | None = None,
    *,
    work_dir: str | Path = ".",
    category: str | None = None,
    limit: int = 12,
) -> dict[str, Any]:
    receipt = receipt or probe_edge(category=category, limit=limit)
    store = default_store_dir(work_dir)
    store.mkdir(parents=True, exist_ok=True)
    data = receipt.to_dict()
    ts = data.get("generated_at", "unknown").replace(":", "-").replace("+", "_")
    path = store / f"edge_{ts}.json"
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    latest = store / "LATEST.json"
    latest.write_text(json.dumps(data, indent=2), encoding="utf-8")
    # index
    index_path = store / "INDEX.jsonl"
    with index_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "generated_at": data.get("generated_at"),
            "ok": data.get("ok_count"),
            "fail": data.get("fail_count"),
            "sha256": data.get("sha256"),
            "file": path.name,
        }) + "\n")
    return {"path": str(path), "latest": str(latest), "receipt": data}


def load_latest(work_dir: str | Path = ".") -> dict[str, Any] | None:
    p = default_store_dir(work_dir) / "LATEST.json"
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def history_summary(work_dir: str | Path = ".", last_n: int = 10) -> dict[str, Any]:
    index = default_store_dir(work_dir) / "INDEX.jsonl"
    if not index.is_file():
        return {"entries": [], "count": 0}
    lines = index.read_text(encoding="utf-8").strip().splitlines()
    entries = []
    for line in lines[-last_n:]:
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return {"entries": entries, "count": len(lines)}
