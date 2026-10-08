"""Regression: an unavailable pinned integration must not be reported green."""

from pathlib import Path
import re


WORKFLOW = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "ci.yml"


def test_pinned_checkout_failure_is_visible_as_a_failed_job():
    text = WORKFLOW.read_text(encoding="utf-8")
    pinned = text.split("  mega-skills-pinned:", 1)[1]
    assert "id: mega_checkout" in pinned
    assert "continue-on-error: true" in pinned
    assert "if: steps.mega_checkout.outcome == 'success'" in pinned
    assert "if: steps.mega_checkout.outcome != 'success'" in pinned
    failure = pinned.split("- name: Fail when pinned proof is unavailable", 1)[1]
    assert re.search(r"(?m)^\s*exit 1\s*$", failure)
    assert "NOT validated" in failure


def test_core_test_matrix_remains_independent_of_optional_checkout():
    text = WORKFLOW.read_text(encoding="utf-8")
    core = text.split("  test:", 1)[1].split("  mega-skills-pinned:", 1)[0]
    assert 'python-version: ["3.11", "3.12", "3.13"]' in core
    assert "pytest --cov=fde_powerhouse" in core
