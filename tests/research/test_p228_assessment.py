"""P228 — readiness assessment is a documentation deliverable.

This is a docs-only guard: it asserts the report exists and carries a valid verdict token. It touches no
pipeline behavior, no severity, no routing.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "documentation/research/assisted_mode/p228_readiness/READINESS_ASSESSMENT.md"

VERDICTS = (
    "A — BUG_BOUNTY_READY",
    "B — READY_WITH_OPERATOR_SUPERVISION",
    "C — RECALL_LIMITED",
    "D — HARNESS_LIMITED",
    "E — ARCHITECTURE_LIMITED",
    "F — NOT_READY",
)


def test_report_exists():
    assert REPORT.exists(), "P228 readiness assessment is missing"


def test_report_has_a_valid_verdict():
    text = REPORT.read_text()
    assert any(v in text for v in VERDICTS), "report has no recognized readiness verdict token"


def test_report_has_a_numeric_readiness_score():
    text = REPORT.read_text()
    assert "Readiness Score" in text and "/ 100" in text
