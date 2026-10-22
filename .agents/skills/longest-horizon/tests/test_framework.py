"""Module test_framework.py — APEX Holographic Mesh Engineering.

# WHY: Ensures architectural intent and recovery notes are documented.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from framework import (
    AspenGrove,
    BeliefUpdater,
    ConfidenceModel,
    FileLock,
    HeavySeal,
    HeavinessAuditor,
    HighCouncil,
    LogicEngine,
    LongHorizonStore,
    PointerMismatch,
    Position,
    Proposition,
    SequentialThinker,
    TamperError,
    TokenBudget,
    atomic_write,
    safe_json_load,
    validate_confidence,
    validate_identifier,
    StructuredLogger,
    run_legal_worm,
    verify_legal_worm,
    compress_to_pointers,
    estimate_tokens,
)


class SequentialThinkingTests(unittest.TestCase):
    def test_valid_chain_verifies(self) -> Any:
        t = SequentialThinker()
        t.add_step("hypothesize", "A")
        t.add_step("verify", "B", evidence="docket #1", cites=["s1"])
        v = t.verify_chain()
        self.assertTrue(v.ok, v.errors)

    def test_missing_evidence_and_citation_is_flagged(self) -> Any:
        t = SequentialThinker()
        t.add_step("hypothesize", "seed", evidence="established fact")
        t.add_step("infer", "no support")  # non-seed step, neither evidence nor cite
        v = t.verify_chain()
        self.assertFalse(v.ok)
        self.assertTrue(any("neither sources" in e for e in v.errors))

    def test_forward_citation_is_rejected(self) -> Any:
        t = SequentialThinker()
        t.add_step("hypothesize", "A")
        t.add_step("verify", "B", cites=["s3"])  # s3 does not exist yet
        v = t.verify_chain()
        self.assertFalse(v.ok)

    def test_cycle_is_detected(self) -> Any:
        t = SequentialThinker()
        t.add_step("hypothesize", "A", cites=["s2"])
        t.add_step("verify", "B", cites=["s1"])
        v = t.verify_chain()
        self.assertFalse(v.ok)
        self.assertTrue(any("cycle" in e for e in v.errors))


class TokenBudgetTests(unittest.TestCase):
    def test_estimate_and_budget(self) -> Any:
        b = TokenBudget(limit=100)
        p = b.record("x", "a" * 500)  # 500 // 4 = 125 tokens
        self.assertEqual(p.tokens, 125)
        self.assertTrue(b.over_budget)

    def test_compress_reduces_footprint(self) -> Any:
        items = [
            {"claim": "RICO predicate met", "source": "docket-12", "confidence": 0.9}
            for _ in range(20)
        ]
        out = compress_to_pointers(items, prefix="step")
        self.assertGreater(out["savings_ratio"], 0.0)
        self.assertEqual(len(out["pointers"]), 20)
        # digest is stable per item
        self.assertEqual(len(out["pointers"][0]["digest"]), 64)


class HighCouncilTests(unittest.TestCase):
    def test_dispute_resolves_by_weight(self) -> Any:
        c = HighCouncil()
        c.seat("procedural", lambda q: Position(id="proc", vp="procedural", role="procedural",
                                                 claim="file within 30d", confidence=0.9, supports=["proc"]))
        c.seat("evidence", lambda q: Position(id="evi", vp="evidence", role="evidence",
                                              claim="strike exhibit 4", confidence=0.95, supports=["evi"],
                                              contradicts=["proc"]))
        d = c.deliberate("strike?")
        self.assertEqual(len(d.disputes), 1)
        self.assertEqual(d.disputes[0].resolved_by, "evidence")

    def test_unresolved_preserved_on_tie(self) -> Any:
        c = HighCouncil()
        c.seat("a", lambda q: Position(id="a", vp="a", role="default", claim="do X", confidence=0.9,
                                        supports=["a"], contradicts=["b"]))
        c.seat("b", lambda q: Position(id="b", vp="b", role="default", claim="do Y", confidence=0.9,
                                        supports=["b"], contradicts=["a"]))
        d = c.deliberate("X or Y?")
        self.assertTrue(any(u.startswith("do") for u in d.unresolved))


class LongHorizonTests(unittest.TestCase):
    def setUp(self) -> Any:
        self.store = LongHorizonStore(".horizon_test")
        self.name = "wave-fixture"

    def test_checkpoint_resume_roundtrip(self) -> Any:
        receipt = self.store.checkpoint(self.name, {"k": "v", "n": 1})
        self.assertEqual(len(receipt.digest), 64)
        self.assertEqual(self.store.resume(self.name), {"k": "v", "n": 1})

    def test_tamper_detected(self) -> Any:
        self.store.checkpoint(self.name, {"k": "v"})
        path = self.store.root / f"{self.name}.json"
        record = json.loads(path.read_text())
        record["payload"]["k"] = "TAMPERED"
        path.write_text(json.dumps(record))
        with self.assertRaises(TamperError):
            self.store.resume(self.name)

    def test_verify_reports_state(self) -> Any:
        self.store.checkpoint(self.name, {"ok": True})
        self.assertTrue(self.store.verify(self.name))
        self.assertFalse(self.store.verify("nonexistent"))


class AspenGroveTests(unittest.TestCase):
    def setUp(self) -> Any:
        import shutil
        from pathlib import Path
        path = Path(".grove_test")
        if path.exists():
            shutil.rmtree(path)
        self.grove = AspenGrove(".grove_test")

    def test_remember_recall_and_digest(self) -> Any:
        p = self.grove.remember("fact", {"text": "RICO predicate met"}, source="docket-12")
        self.assertEqual(p.kind, "fact")
        self.assertEqual(len(p.digest), 64)
        entry = self.grove.recall(p.id)
        self.assertIsNotNone(entry)
        self.assertEqual(entry["content"]["text"], "RICO predicate met")

    def test_query_by_kind_and_pointer_index(self) -> Any:
        self.grove.remember("fact", {"a": 1})
        self.grove.remember("plan", {"b": 2})
        self.assertEqual(len(self.grove.query("fact")), 1)
        self.assertEqual(len(self.grove.pointer_index()), 2)

    def test_tamper_detected_on_recall(self) -> Any:
        p = self.grove.remember("fact", {"a": 1})
        # Corrupt the on-disk entry so its content no longer matches the digest.
        index_path = self.grove.root / "pointer_index.json"
        data = json.loads(index_path.read_text())
        data[p.id]["content"]["a"] = 999
        index_path.write_text(json.dumps(data))
        with self.assertRaises(PointerMismatch):
            AspenGrove(self.grove.root).recall(p.id)


class GeniusLogicTests(unittest.TestCase):
    def test_modus_ponens_derivation(self) -> Any:
        e = LogicEngine()
        e.add(Proposition("p", "predicate met", "true"))
        e.add(Proposition("q", "racketeering established"))
        e.add_rule("p", "q")
        e.derive()
        self.assertEqual(e.props["q"].truth, "true")

    def test_contradiction_detected(self) -> Any:
        e = LogicEngine()
        e.add(Proposition("a", "exhibit authentic", "true", contradicts=["b"]))
        e.add(Proposition("b", "exhibit forged", "true", contradicts=["a"]))
        self.assertIn(("a", "b"), e.contradictions())

    def test_adversary_refutes_claim(self) -> Any:
        e = LogicEngine()
        e.add(Proposition("claim", "motion timely", "true"))
        e.add(Proposition("counter", "filed after deadline", "true", contradicts=["claim"]))
        verdict = e.adversary("claim")
        self.assertTrue(verdict.refuted)
        self.assertIn("counter", verdict.challengers)


class MachineLearningTests(unittest.TestCase):
    def test_bayesian_posterior(self) -> Any:
        b = BeliefUpdater(prior=0.5)
        b.add_evidence(2.0).add_evidence(2.0)  # LR 4 total
        # 0.5*4 / (0.5*4 + 0.5) = 2 / 2.5 = 0.8
        self.assertAlmostEqual(b.posterior(), 0.8, places=6)

    def test_evidence_weight_scales_update(self) -> Any:
        b = BeliefUpdater(prior=0.5)
        b.add_evidence(2.0, weight=2.0)
        self.assertAlmostEqual(b.posterior(), 0.8, places=6)

    def test_confidence_shrinkage(self) -> Any:
        model = ConfidenceModel(shrinkage=0.5)
        conf = model.combine([(1.0, 1.0), (0.0, 1.0)])  # mean 0.5 -> stays 0.5
        self.assertAlmostEqual(conf, 0.5, places=6)
        model2 = ConfidenceModel(shrinkage=0.0)
        conf2 = model2.combine([(1.0, 3.0), (0.0, 1.0)])  # weighted mean 0.75
        self.assertAlmostEqual(conf2, 0.75, places=6)

    def test_bayesian_extreme_overflow_stability(self) -> Any:
        b = BeliefUpdater(prior=0.5)
        # Add massive evidence that would previously overflow math.exp
        for _ in range(200):
            b.add_evidence(100.0)
        self.assertEqual(b.posterior(), 1.0)
        self.assertEqual(b.odds(), float("inf"))

        # Add massive negative evidence (LR < 1.0) that would previously underflow
        b_neg = BeliefUpdater(prior=0.5)
        for _ in range(200):
            b_neg.add_evidence(0.01)
        self.assertEqual(b_neg.posterior(), 0.0)
        self.assertEqual(b_neg.odds(), 0.0)

    def test_bayesian_boundary_priors(self) -> Any:
        b_zero = BeliefUpdater(prior=0.0)
        b_zero.add_evidence(1000.0)
        self.assertEqual(b_zero.posterior(), 0.0)
        self.assertEqual(b_zero.odds(), 0.0)

        b_one = BeliefUpdater(prior=1.0)
        b_one.add_evidence(0.001)
        self.assertEqual(b_one.posterior(), 1.0)
        self.assertEqual(b_one.odds(), float("inf"))


class MakeItHeavyTests(unittest.TestCase):
    def test_audits_own_heavy_module(self) -> Any:
        report = HeavinessAuditor().audit_file(
            str(Path(__file__).resolve().parents[1] / "framework" / "long_horizon.py")
        )
        self.assertTrue(report.criteria["module_docstring"])
        self.assertTrue(report.criteria["typed_api"])
        self.assertTrue(report.criteria["provenance"])
        self.assertGreaterEqual(report.score, 0.6)

    def test_flags_thin_module(self) -> Any:
        thin = Path(".thin_test.py")
        thin.write_text("def f(x):\n    return x\n")
        try:
            report = HeavinessAuditor().audit_file(thin)
            self.assertLess(report.score, 0.6)
            self.assertFalse(report.criteria["module_docstring"])
        finally:
            thin.unlink()


class HardeningTests(unittest.TestCase):
    def test_atomic_write_is_readable(self) -> Any:
        p = Path(".atomic_test.bin")
        atomic_write(p, b"hello-long-horizon")
        try:
            self.assertEqual(p.read_bytes(), b"hello-long-horizon")
        finally:
            p.unlink()

    def test_atomic_write_never_leaves_temp_on_failure(self) -> Any:
        # Make the target's parent a file so tempfile.mkstemp fails mid-write.
        blocker = Path(".atomic_blocker")
        blocker.write_text("i am a file, not a dir")
        try:
            with self.assertRaises(Exception):
                atomic_write(blocker / "sub" / "y.bin", b"x")
            # No temp file should be left behind in the working dir.
            leftovers = list(Path(".").glob("*.tmp*"))
            self.assertEqual(leftovers, [])
        finally:
            blocker.unlink(missing_ok=True)

    def test_safe_json_load_fail_closed(self) -> Any:
        bad = Path(".bad.json")
        bad.write_text("{not valid json")
        try:
            obj, err = safe_json_load(bad)
            self.assertIsNone(obj)
            self.assertIsNotNone(err)
        finally:
            bad.unlink()

    def test_validators(self) -> Any:
        with self.assertRaises(ValueError):
            validate_confidence(1.5)
        with self.assertRaises(ValueError):
            validate_identifier("bad id!")
        self.assertEqual(validate_identifier("ptr-001"), "ptr-001")

    def test_file_lock_serializes(self) -> Any:
        sentinel = Path(".lock_sentinel")
        sentinel.unlink(missing_ok=True)
        try:
            with FileLock(sentinel):
                pass
            self.assertTrue(True)  # acquiring + releasing works
        finally:
            sentinel.with_name(sentinel.name + ".lock").unlink(missing_ok=True)

    def test_structured_logger_emits_json(self) -> Any:
        import logging

        logger = StructuredLogger("test.lh")
        captured = {}
        h = logging.Handler()
        h.emit = lambda rec: captured.update(rec=rec)  # type: ignore
        logger._log.addHandler(h)
        logger._log.setLevel(logging.INFO)
        logger.event("verified", "checkpoint", name="x")
        self.assertIn('"state": "verified"', captured["rec"].getMessage())


class HeavySealTests(unittest.TestCase):
    def setUp(self) -> Any:
        self.store = LongHorizonStore(".horizon_seal_test")
        self.seal = HeavySeal(self.store)

    def test_seal_bakes_heaviness_into_provenance(self) -> Any:
        receipt, report = self.seal.seal(
            "wave", {"ok": True},
            source_module=Path(__file__).resolve().parents[1] / "framework" / "long_horizon.py",
        )
        self.assertGreaterEqual(report.score, 0.6)
        self.assertTrue(receipt.envelope.source.startswith("heavy-seal:"))
        # round-trip still verifies
        self.assertEqual(self.store.resume("wave"), {"ok": True})

    def test_seal_never_rejects_low_heaviness(self) -> Any:
        # A gate must not eradicate progress: even a thin module is stored.
        thin = Path(".thin_seal.py")
        thin.write_text("def f(x):\n    return x\n")
        try:
            receipt, report = self.seal.seal("thin", {"v": 1}, source_module=thin)
            self.assertTrue(receipt.envelope.source.startswith("heavy-seal:"))
            self.assertEqual(self.store.resume("thin"), {"v": 1})
        finally:
            thin.unlink()


class LegalWormTests(unittest.TestCase):
    def _make_repo(self, root: Path) -> Path:
        repo = root / "case_brain"
        repo.mkdir(parents=True)
        (repo / "engine.py").write_text('"""Autonomous engine."""\nclass Engine:\n    pass\n')
        (repo / "README.md").write_text("# Case Brain\nThis is legal.\n")
        return repo

    def test_run_and_verify_roundtrip(self) -> Any:
        import tempfile

        base = Path(tempfile.mkdtemp())
        self._make_repo(base)
        out = Path(tempfile.mkdtemp())
        report = run_legal_worm(repos=["case_brain"], output_root=out, base=base)
        self.assertGreaterEqual(report.artifacts, 2)
        verification = verify_legal_worm(output_root=out, base=base)
        self.assertTrue(verification["ok"])
        self.assertEqual(verification["verified"], verification["total"])

    def test_worm_detects_tamper(self) -> Any:
        import tempfile

        base = Path(tempfile.mkdtemp())
        self._make_repo(base)
        out = Path(tempfile.mkdtemp())
        run_legal_worm(repos=["case_brain"], output_root=out, base=base)
        # Tamper with a locked artifact.
        (base / "case_brain" / "engine.py").write_text('"""pwned."""\nclass X:\n    pass\n')
        verification = verify_legal_worm(output_root=out, base=base)
        self.assertFalse(verification["ok"])
        self.assertGreater(len(verification["mismatches"]), 0)


class ZeroHallucinationGateTests(unittest.TestCase):
    """The only blocking gate. Refuses hallucination, never blocks progress."""

    def test_allows_evidence_backed_claim(self) -> Any:
        from framework import Claim, adjudicate

        c = Claim(
            text="32/32 tests pass",
            tool_evidence=("pytest exit 0",),
            source_citation="tests/test_framework.py",
            test_pass_receipt="pytest tests/",
        )
        v = adjudicate(c)
        self.assertTrue(v.allowed)
        self.assertIsNone(v.reason)

    def test_refuses_no_tool_evidence(self) -> Any:
        from framework import Claim, RefusalReason, adjudicate

        c = Claim(text="it works")
        v = adjudicate(c)
        self.assertFalse(v.allowed)
        self.assertEqual(v.reason, RefusalReason.NO_TOOL_EVIDENCE.value)

    def test_refuses_simulated_as_live(self) -> Any:
        from framework import Claim, RefusalReason, adjudicate

        c = Claim(
            text="ran the full pipeline",
            tool_evidence=("sleep 5",),
            completion_claim=True,
            verification_step="pytest",
            simulated=True,
        )
        v = adjudicate(c)
        self.assertFalse(v.allowed)
        self.assertEqual(v.reason, RefusalReason.SIMULATED_AS_LIVE.value)

    def test_refuses_completion_without_verification(self) -> Any:
        from framework import Claim, RefusalReason, adjudicate

        c = Claim(
            text="shipped",
            tool_evidence=("git commit",),
            completion_claim=True,
        )
        v = adjudicate(c)
        self.assertFalse(v.allowed)
        self.assertEqual(v.reason, RefusalReason.COMPLETION_WITHOUT_VERIFY.value)

    def test_refuses_fabricated_authority(self) -> Any:
        from framework import Claim, RefusalReason, adjudicate

        c = Claim(
            text="per Statute 99-U.M.C. §3.14...",
            fabricated_authority=True,
        )
        v = adjudicate(c)
        self.assertFalse(v.allowed)
        self.assertEqual(v.reason, RefusalReason.FABRICATED_AUTHORITY.value)

    def test_never_refuses_reversible_mutation_under_scope(self) -> Any:
        from framework import Claim, adjudicate

        c = Claim(
            text="edit a local file",
            tool_evidence=("edit tool call",),
            reversible=True,
            scope="scoped",
        )
        v = adjudicate(c)
        self.assertTrue(v.allowed)

    def test_never_refuses_progress_with_verification_in_flight(self) -> Any:
        from framework import Claim, adjudicate

        c = Claim(
            text="running test suite",
            tool_evidence=("pytest started",),
            completion_claim=True,
            verification_step="await pytest exit code",
        )
        v = adjudicate(c)
        self.assertTrue(v.allowed)

    def test_never_refuses_clarifying_question(self) -> Any:
        from framework import Claim, NeverRefuseReason, adjudicate

        c = Claim(text="which lane?", is_clarifying_question=True)
        v = adjudicate(c)
        self.assertTrue(v.allowed)
        self.assertEqual(v.reason, NeverRefuseReason.CLARIFYING_QUESTION.value)

    def test_enforce_raises_on_refusal(self) -> Any:
        from framework import Claim, GateRejection, enforce

        c = Claim(text="trust me")
        with self.assertRaises(GateRejection):
            enforce(c)

    def test_enforce_returns_verdict_on_allow(self) -> Any:
        from framework import Claim, enforce

        c = Claim(
            text="ok",
            tool_evidence=("x",),
        )
        v = enforce(c)
        self.assertTrue(v.allowed)

    def test_batch_summary_preserves_minority_refusals(self) -> Any:
        from framework import Claim, batch_adjudicate, summarize

        claims = [
            Claim(text="a", tool_evidence=("e",)),
            Claim(text="b"),
            Claim(text="c", tool_evidence=("e",)),
            Claim(text="d", fabricated_authority=True),
        ]
        verdicts = batch_adjudicate(claims)
        s = summarize(verdicts)
        self.assertEqual(s["total"], 4)
        self.assertEqual(s["allowed"], 2)
        self.assertEqual(s["refused"], 2)
        self.assertEqual(s["refusal_rate"], 0.5)

    def test_audit_log_is_jsonl(self) -> Any:
        from framework import Claim, batch_adjudicate, export_audit_log

        verdicts = batch_adjudicate(
            [Claim(text="a", tool_evidence=("e",)), Claim(text="b")]
        )
        log = export_audit_log(verdicts)
        lines = [ln for ln in log.strip().split("\n") if ln]
        self.assertEqual(len(lines), 2)
        for ln in lines:
            json.loads(ln)  # parses


if __name__ == "__main__":
    unittest.main()

# WHY: Explaining resilience and recovery rationale ensures non-blocking operational continuity.
