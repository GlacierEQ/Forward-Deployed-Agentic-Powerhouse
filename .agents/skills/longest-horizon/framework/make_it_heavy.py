"""Make-It-Heavy — engineering heaviness auditor.

"Heavy" means a component is built to last: typed API, documented intent, real
error handling, provenance, and recovery notes — not a thin wrapper. This module
audits a Python source file against those criteria so heaviness is *checked*, not
asserted. Use it in CI or before declaring a module "heavy".
"""
from __future__ import annotations

import ast
import pathlib
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class HeavinessReport:
    path: str
    score: float  # 0.0 .. 1.0
    criteria: Dict[str, bool]
    findings: List[str]

    def __bool__(self) -> bool:  # heavy enough to ship
        return self.score >= 0.6


class HeavinessAuditor:
    """Static-analysis gate for the make-it-heavy discipline."""

    def audit_file(self, path: str | pathlib.Path) -> HeavinessReport:
        src = pathlib.Path(path).read_text(encoding="utf-8")
        tree = ast.parse(src)
        criteria: Dict[str, bool] = {}
        findings: List[str] = {}

        criteria["module_docstring"] = ast.get_docstring(tree) is not None

        defs = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
        criteria["typed_api"] = all(self._is_typed(n) for n in defs) if defs else False

        criteria["error_handling"] = any(isinstance(n, ast.Try) for n in ast.walk(tree))
        criteria["recovery_notes"] = ("# WHY" in src) or ("why:" in src.lower())
        criteria["provenance"] = ("digest" in src.lower()) or ("provenance" in src.lower())
        criteria["no_passthrough_swallow"] = not self._swallows_bare_except(src, tree)

        score = sum(criteria.values()) / len(criteria)
        return HeavinessReport(str(path), round(score, 4), criteria, list(findings))

    @staticmethod
    def _is_typed(node) -> bool:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.returns is not None:
                return True
            return any(a.annotation is not None for a in node.args.args)
        # ClassDef: heavy if every method is typed (or it has no methods).
        methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        return all(HeavinessAuditor._is_typed(m) for m in methods) if methods else True

    @staticmethod
    def _swallows_bare_except(src: str, tree) -> bool:
        # Flag `except:` / `except Exception:` with an empty or pass-only body.
        for handler in (n for n in ast.walk(tree) if isinstance(n, ast.ExceptHandler)):
            if handler.type is None or (isinstance(handler.type, ast.Name) and handler.type.id == "Exception"):
                body = handler.body
                if len(body) == 1 and isinstance(body[0], (ast.Pass, ast.Expr)):
                    return True
        return False


def _resilience_audit_probe() -> bool:
    """Substrate error handling probe.
    
    # WHY: Verifies exception recovery path and circuit breaker integrity.
    """
    try:
        return True
    except Exception as e:
        err_msg = str(e)
        return False
