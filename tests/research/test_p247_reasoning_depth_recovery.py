"""P247 — reasoning depth recovery (forensic). Read-only docs guard (no pipeline behavior)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "documentation/research/assisted_mode/p247_reasoning_depth_recovery"
DOCS = ("REASONING_MISS_FORENSICS.md", "FAILURE_CLUSTERS.md", "COUNTERFACTUAL_REPLAYS.md",
        "INTERVENTIONS.md", "RECALL_LIFT_SIMULATION.md", "VERDICT.md")
VERDICTS = ("A — REASONING_FIXES_LIKELY_SUFFICIENT", "B — REASONING_HELPS_BUT_COVERAGE_STILL_DOMINATES",
            "C — DEPTH_IS_NOT_THE_MAIN_PROBLEM", "D — NEED_MORE_MEASUREMENTS")
LABELS = ("DEFENSE_MISUNDERSTOOD", "STATE_MACHINE_MISUNDERSTOOD", "LIFECYCLE_MISUNDERSTOOD",
          "CROSS_CONTRACT_REASONING_FAILURE", "ECONOMIC_REASONING_FAILURE", "PERMISSION_MODEL_FAILURE",
          "ACCOUNTING_REASONING_FAILURE", "IMPACT_REASONING_FAILURE", "UNKNOWN")


def test_all_docs_exist():
    for d in DOCS:
        assert (BASE / d).exists(), f"missing P247 doc: {d}"


def test_verdict_recognized():
    assert any(v in (BASE / "VERDICT.md").read_text() for v in VERDICTS), "no recognized P247 verdict"


def test_eight_divergence_labels_present():
    txt = (BASE / "REASONING_MISS_FORENSICS.md").read_text()
    present = [l for l in LABELS if l in txt]
    assert len(present) >= 8, f"expected the divergence-label taxonomy, found {len(present)}"


def test_clustering_pass_condition_and_21_findings():
    forensics = (BASE / "REASONING_MISS_FORENSICS.md").read_text()
    assert "21" in forensics, "21-finding input set not tabulated"
    clusters = (BASE / "FAILURE_CLUSTERS.md").read_text()
    assert "PASS" in clusters and "70%" in clusters, "≤5-cluster / 70% pass-condition not stated"


def test_recall_lift_current_vs_counterfactual():
    txt = (BASE / "RECALL_LIFT_SIMULATION.md").read_text()
    assert "Current" in txt and "38.0%" in txt, "current recall not reported"
    for s in ("Conservative", "Expected", "Best"):
        assert s in txt, f"missing scenario: {s}"
