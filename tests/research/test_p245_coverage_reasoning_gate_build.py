"""P245 — coverage + reasoning-depth gate BUILD. Docs guard (no pipeline behavior)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "documentation/research/assisted_mode/p245_coverage_reasoning_gate_build"
REPORTS = ("BUILD_REPORT.md", "VALIDATION_NEXTGEN.md", "VALIDATION_DITTOETH.md",
           "OPERATOR_BURDEN.md", "SAFETY_REPORT.md")
VERDICTS = (
    "A — READY_FOR_DEFAULT_OFF_USE",
    "B — WORKS_BUT_TOO_HEAVY",
    "C — NEEDS_REFINEMENT",
    "D — REJECT_GATE",
)


def test_all_reports_exist():
    for r in REPORTS:
        assert (BASE / r).exists(), f"missing P245 report: {r}"


def test_build_report_has_recognized_verdict():
    txt = (BASE / "BUILD_REPORT.md").read_text()
    assert any(v in txt for v in VERDICTS), "no recognized P245 verdict token"


def test_validation_reports_recall_gain_metric():
    txt = (BASE / "VALIDATION_NEXTGEN.md").read_text()
    assert "coverage_enforced_recall_gain" in txt, "validation must report the recall-gain metric"
    # the four outcome labels the user asked for
    for lbl in ("would it have been triaged", "forced", "new_candidate", "no_change"):
        assert lbl in txt, f"recall-gain table missing '{lbl}'"


def test_safety_report_asserts_default_off_and_hashes():
    txt = (BASE / "SAFETY_REPORT.md").read_text()
    assert "Default-off" in txt and "Forbidden file hashes preserved" in txt


def test_dittoeth_validation_has_diamond_verdict():
    txt = (BASE / "VALIDATION_DITTOETH.md").read_text()
    diamond_verdicts = ("A — GENERALIZES_TO_DIAMOND_FACETS", "B — WORKS_BUT_NEEDS_TUNING",
                        "C — TOO_HEAVY_ON_DIAMONDS", "D — FAILS_TO_COVER_DITTOETH_MISS_MODE")
    assert any(v in txt for v in diamond_verdicts), "no recognized dittoeth verdict token"
    assert "coverage_enforced_recall_gain" in txt
