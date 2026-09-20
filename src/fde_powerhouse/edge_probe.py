"""Public edge probe — HEAD/GET homepage reachability with receipts.

Public-only. No content scraping claims. Timeouts hard. Rate limited by sample size.
"""

from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from .leading_edge import all_homepages, by_category

USER_AGENT = "FDE-Powerhouse-EdgeProbe/0.5 (+https://github.com/GlacierEQ/Forward-Deployed-Agentic-Powerhouse)"


@dataclass
class ProbeItem:
    id: str
    homepage: str
    category: str
    ok: bool
    status_code: int | None = None
    error: str | None = None
    latency_ms: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EdgeProbeReceipt:
    generated_at: str
    sample_size: int
    ok_count: int
    fail_count: int
    items: list[ProbeItem] = field(default_factory=list)
    sha256: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = {
            "generated_at": self.generated_at,
            "sample_size": self.sample_size,
            "ok_count": self.ok_count,
            "fail_count": self.fail_count,
            "items": [i.to_dict() for i in self.items],
        }
        payload = json.dumps(d, sort_keys=True, default=str)
        d["sha256"] = hashlib.sha256(payload.encode()).hexdigest()
        return d


def _one(url: str, timeout: float) -> tuple[bool, int | None, str | None, float]:
    import time

    start = time.perf_counter()
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = getattr(resp, "status", None) or resp.getcode()
            ms = (time.perf_counter() - start) * 1000
            return True, int(code), None, ms
    except urllib.error.HTTPError as exc:
        ms = (time.perf_counter() - start) * 1000
        # Some hosts reject HEAD; try GET minimal
        if exc.code in (405, 403, 501):
            try:
                greq = urllib.request.Request(
                    url, method="GET", headers={"User-Agent": USER_AGENT}
                )
                with urllib.request.urlopen(greq, timeout=timeout) as resp:
                    code = getattr(resp, "status", None) or resp.getcode()
                    ms = (time.perf_counter() - start) * 1000
                    return True, int(code), None, ms
            except Exception as exc2:  # noqa: BLE001
                return False, getattr(exc, "code", None), str(exc2)[:200], ms
        return False, exc.code, str(exc)[:200], ms
    except Exception as exc:  # noqa: BLE001
        ms = (time.perf_counter() - start) * 1000
        return False, None, str(exc)[:200], ms


def probe_edge(
    *,
    category: str | None = None,
    limit: int = 12,
    timeout: float = 5.0,
    workers: int = 6,
) -> EdgeProbeReceipt:
    if category:
        raw = [
            {"id": s.get("id", ""), "name": s.get("name", ""), "homepage": s.get("homepage", ""), "category": category}
            for s in by_category(category)
        ]
    else:
        raw = all_homepages()
    sample = [r for r in raw if r.get("homepage")][: max(1, limit)]

    items: list[ProbeItem] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futs = {
            pool.submit(_one, r["homepage"], timeout): r for r in sample
        }
        for fut in as_completed(futs):
            r = futs[fut]
            ok, code, err, ms = fut.result()
            items.append(
                ProbeItem(
                    id=r.get("id", ""),
                    homepage=r["homepage"],
                    category=r.get("category", ""),
                    ok=ok,
                    status_code=code,
                    error=err,
                    latency_ms=round(ms, 1) if ms is not None else None,
                )
            )

    items.sort(key=lambda x: (x.category, x.id))
    ok_count = sum(1 for i in items if i.ok)
    receipt = EdgeProbeReceipt(
        generated_at=datetime.now(timezone.utc).isoformat(),
        sample_size=len(items),
        ok_count=ok_count,
        fail_count=len(items) - ok_count,
        items=items,
    )
    # populate sha
    receipt.sha256 = receipt.to_dict()["sha256"]
    return receipt
