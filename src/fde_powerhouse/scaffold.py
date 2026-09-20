"""Ground-up agent scaffold — production-leaning field agent pack."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .plan import CyclePlan


def write_scaffold(root: Path, plan: CyclePlan) -> dict[str, Any]:
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    files: dict[str, str] = {}

    files["IDENTITY.md"] = f"""# Identity — Forward Deployed Agentic AI

**Target:** {plan.target}  
**Mode:** {plan.mode}  
**Problem:** {plan.problem or "(unspecified)"}

## Law

- Full power + dual-plane honesty
- Operator intent over document theater
- `approval_packet_only` for deploy/merge/network
- Hash-bound receipts for every cycle stage
"""

    files["PLAN.yaml"] = f"""mode: {plan.mode}
target: {plan.target}
problem: |
  {plan.problem or ""}
skill_targets:
""" + "".join(f"  - {s}\n" for s in plan.skill_targets) + "pipeline_hints:\n" + "".join(
        f"  - {p}\n" for p in plan.pipeline_hints
    )

    files["src/agent/__init__.py"] = '"""Field agent package."""\n__version__ = "0.1.0"\n'

    files["src/agent/orchestrator.py"] = '''"""Production-leaning orchestrator — tool loop with policy gates."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from .policy import PolicyEngine, PolicyDecision
from .memory_port import MemoryPort
from .tools import ToolRegistry


@dataclass
class TurnResult:
    ok: bool
    output: str
    tools_used: list[str] = field(default_factory=list)
    policy: list[dict[str, Any]] = field(default_factory=list)
    receipt: dict[str, Any] = field(default_factory=dict)


class Orchestrator:
    """Minimal but real loop: plan → policy → tool → memory → receipt."""

    def __init__(
        self,
        policy: PolicyEngine | None = None,
        memory: MemoryPort | None = None,
        tools: ToolRegistry | None = None,
    ) -> None:
        self.policy = policy or PolicyEngine()
        self.memory = memory or MemoryPort()
        self.tools = tools or ToolRegistry.default()

    def run(self, goal: str, max_steps: int = 8) -> TurnResult:
        self.memory.write("working", {"goal": goal})
        tools_used: list[str] = []
        policy_log: list[dict[str, Any]] = []
        outputs: list[str] = []

        for step in range(max_steps):
            action = self._select_action(goal, step)
            decision = self.policy.evaluate(action)
            policy_log.append(decision.to_dict())
            if not decision.allowed:
                outputs.append(f"blocked:{action['type']}:{decision.reason}")
                break
            result = self.tools.execute(action)
            tools_used.append(action["type"])
            outputs.append(str(result.get("output", "")))
            self.memory.write("episodic", {"step": step, "action": action, "result": result})
            if result.get("done"):
                break

        receipt = {
            "goal": goal,
            "steps": len(tools_used),
            "tools_used": tools_used,
            "deploy_mode": "approval_packet_only",
        }
        return TurnResult(
            ok=True,
            output="\n".join(outputs) or "noop",
            tools_used=tools_used,
            policy=policy_log,
            receipt=receipt,
        )

    def _select_action(self, goal: str, step: int) -> dict[str, Any]:
        if step == 0:
            return {"type": "recall", "query": goal}
        if step == 1:
            return {"type": "analyze", "goal": goal}
        if step == 2:
            return {"type": "propose", "goal": goal}
        return {"type": "done", "goal": goal}
'''

    files["src/agent/policy.py"] = '''"""Policy engine — fail-closed tool gates."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

FORBIDDEN = frozenset({
    "git_push",
    "git_merge",
    "network_send",
    "credential_read",
    "force_delete",
})


@dataclass
class PolicyDecision:
    allowed: bool
    reason: str
    action_type: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "action_type": self.action_type,
        }


class PolicyEngine:
    def evaluate(self, action: dict[str, Any]) -> PolicyDecision:
        t = str(action.get("type", ""))
        if t in FORBIDDEN:
            return PolicyDecision(False, f"forbidden action: {t}", t)
        if t.startswith("deploy") or t.startswith("merge"):
            return PolicyDecision(False, "approval_packet_only — human gate required", t)
        return PolicyDecision(True, "ok", t)
'''

    files["src/agent/memory_port.py"] = '''"""Memory port — working / episodic / semantic tiers (local)."""

from __future__ import annotations

from typing import Any


class MemoryPort:
    def __init__(self) -> None:
        self._store: dict[str, list[Any]] = {
            "working": [],
            "episodic": [],
            "semantic": [],
            "graph": [],
        }

    def write(self, tier: str, item: Any) -> None:
        if tier not in self._store:
            self._store[tier] = []
        self._store[tier].append(item)

    def read(self, tier: str, limit: int = 20) -> list[Any]:
        return list(self._store.get(tier, [])[-limit:])

    def snapshot(self) -> dict[str, int]:
        return {k: len(v) for k, v in self._store.items()}
'''

    files["src/agent/tools.py"] = '''"""Tool registry — safe local tools only by default."""

from __future__ import annotations

from typing import Any, Callable


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {}

    def register(self, name: str, fn: Callable[[dict[str, Any]], dict[str, Any]]) -> None:
        self._tools[name] = fn

    def execute(self, action: dict[str, Any]) -> dict[str, Any]:
        t = str(action.get("type", ""))
        if t == "done":
            return {"output": "complete", "done": True}
        fn = self._tools.get(t)
        if fn is None:
            return {"output": f"unknown_tool:{t}", "done": False}
        return fn(action)

    @classmethod
    def default(cls) -> "ToolRegistry":
        reg = cls()

        def recall(action: dict[str, Any]) -> dict[str, Any]:
            return {"output": f"recalled:{action.get('query', '')}", "done": False}

        def analyze(action: dict[str, Any]) -> dict[str, Any]:
            return {"output": f"analyzed:{action.get('goal', '')}", "done": False}

        def propose(action: dict[str, Any]) -> dict[str, Any]:
            return {"output": f"proposal:{action.get('goal', '')}", "done": False}

        reg.register("recall", recall)
        reg.register("analyze", analyze)
        reg.register("propose", propose)
        return reg
'''

    files["tests/test_agent_loop.py"] = '''"""Agent loop smoke tests."""

from agent.orchestrator import Orchestrator
from agent.policy import PolicyEngine


def test_orchestrator_runs():
    orch = Orchestrator()
    result = orch.run("ship field capability")
    assert result.ok
    assert result.receipt["deploy_mode"] == "approval_packet_only"


def test_policy_blocks_push():
    eng = PolicyEngine()
    d = eng.evaluate({"type": "git_push"})
    assert d.allowed is False
'''

    files["README.md"] = f"""# {plan.target} — FDE field agent

Scaffolded by Forward-Deployed-Agentic-Powerhouse.

```bash
PYTHONPATH=src python -c "from agent.orchestrator import Orchestrator; print(Orchestrator().run('demo'))"
```

Policy: approval_packet_only. Memory tiers: working/episodic/semantic/graph.
"""

    written = []
    for rel, content in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(str(path))

    return {"root": str(root), "count": len(written), "files": written}
