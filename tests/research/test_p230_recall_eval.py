"""P230 — architecture recall generalization evaluation is a documentation deliverable.

Docs-only guard: the report exists with a valid verdict token, and the three captured candidate artifacts exist.
Touches no pipeline behavior, no severity, no routing.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "documentation/research/assisted_mode/p230_recall_generalization"
REPORT = BASE / "RECALL_GENERALIZATION_EVALUATION.md"
ARTIFACTS = [BASE / f"candidates_{s}.md" for s in ("quantamm", "decent", "traitforge")]

VERDICTS = (
    "A — RECALL_GENERALIZES",
    "B — RECALL_PARTIALLY_GENERALIZES",
    "C — RECALL_LENDING_BIASED",
    "D — RECALL_INSUFFICIENT",
)


def test_report_exists():
    assert REPORT.exists(), "P230 recall generalization report is missing"


def test_report_has_valid_verdict():
    text = REPORT.read_text()
    assert any(v in text for v in VERDICTS), "no recognized recall verdict token"


def test_report_has_recall_score():
    text = REPORT.read_text()
    assert "Recall Score" in text and "/ 100" in text


def test_candidate_artifacts_exist():
    for a in ARTIFACTS:
        assert a.exists(), f"missing measurement artifact: {a.name}"
