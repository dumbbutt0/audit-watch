"""P236 — recall gap classification. Docs guard only (read-only analysis phase; no pipeline behavior)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = (
    ROOT
    / "documentation/research/assisted_mode/p236_recall_gap_classification/RECALL_GAP_CLASSIFICATION.md"
)

VERDICTS = (
    "A — SINGLE_FAMILY_GAP",
    "B — FEW_FAMILY_GAPS",
    "C — SCATTERED_GAPS",
    "D — CONTEST_SPECIFIC",
)
NEXT_PHASES = (
    "Build Safe-management lens",
    "Build hostile-token lens",
    "Build lifecycle model",
    "Build reentrancy model",
    "Run second shadow contest first",
)
DELIVERABLE_SECTIONS = (
    "Miss Classification Table",
    "Near-Miss Distribution",
    "Family Clusters",
    "Generalization Score",
    "Final Verdict",
    "Recommended Next Phase",
)


def test_report_exists_with_verdict_and_recommendation():
    assert REPORT.exists(), "P236 classification report missing"
    txt = REPORT.read_text()
    assert any(v in txt for v in VERDICTS), "no recognized P236 verdict token"
    assert any(p in txt for p in NEXT_PHASES), "no recognized recommended-next-phase token"


def test_report_has_required_sections():
    txt = REPORT.read_text()
    for sec in DELIVERABLE_SECTIONS:
        assert sec in txt, f"missing required section: {sec}"


def test_report_classifies_each_awarded_high():
    txt = REPORT.read_text()
    for hid in ("H-01", "H-02", "H-03", "H-04", "H-05"):
        assert hid in txt, f"awarded High {hid} not referenced in classification"
