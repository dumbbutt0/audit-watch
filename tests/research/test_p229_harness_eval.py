"""P229 — integration harness readiness evaluation is a documentation deliverable.

Docs-only guard: the report exists, carries a YES/NO final answer, and includes the taxonomy tally. Touches no
pipeline behavior, no severity, no routing.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "documentation/research/assisted_mode/p229_harness_readiness/INTEGRATION_HARNESS_EVALUATION.md"


def test_report_exists():
    assert REPORT.exists(), "P229 integration harness evaluation is missing"


def test_report_has_final_answer():
    text = REPORT.read_text()
    assert "Answer:" in text and ("**NO.**" in text or "**YES.**" in text)


def test_report_has_taxonomy_tally():
    text = REPORT.read_text()
    for cat in ("isolated library", "single-contract stateful", "lifecycle-driven", "protocol-integration"):
        assert cat in text, f"taxonomy missing category: {cat}"
