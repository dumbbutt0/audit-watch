"""P243 — miss-family ROI audit. Read-only docs guard (no pipeline behavior)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "documentation/research/assisted_mode/p243_miss_roi_audit/MISS_ROI_AUDIT.md"

VERDICTS = (
    "A — COVERAGE_IS_DOMINANT",
    "B — FEW_HIGH_ROI_FAMILIES_REMAIN",
    "C — REASONING_DEPTH_DOMINANT",
    "D — PROOF_CONVERSION_DOMINANT",
    "E — MIXED",
)
SATURATION_BUCKETS = ("Coverage-Bound", "Family-Bound", "Reasoning-Bound", "Proof-Bound")


def test_report_exists_with_verdict():
    assert REPORT.exists(), "P243 ROI audit report missing"
    assert any(v in REPORT.read_text() for v in VERDICTS), "no recognized P243 verdict token"


def test_saturation_buckets_present():
    txt = REPORT.read_text()
    for b in SATURATION_BUCKETS:
        assert b in txt, f"missing saturation bucket: {b}"


def test_has_ranked_recommendation_and_counterfactual():
    txt = REPORT.read_text()
    assert "Counterfactual recall" in txt
    assert "## Recommendation" in txt
    assert "1. **Full-surface coverage enforcement**" in txt, "ranked recommendation #1 missing"
