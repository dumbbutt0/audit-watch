"""P265 — shadow-mode operational trial. Guard test (research-only, measurement-only).

Asserts: deliverable docs exist + recognized verdict; FP=0 and guard PASS across all 13 trial outputs; every
advisory candidate carries 0 promotion flags; the frozen harness/P260/P262 modules+configs are byte-identical
(no tuning during the trial); aggregate metrics present and internally consistent.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "documentation/research/assisted_mode/p265_shadow_operational_trial"
OUT = BASE / "outputs"
DOCS = ("SETUP.md", "TRIAL_PROTOCOL.md", "METRICS.md", "RECALL_DELTA_ANALYSIS.md",
        "OPERATOR_USEFULNESS.md", "NOISE_ANALYSIS.md", "LIMITATIONS.md", "VERDICT.md")
DECISIONS = ("KEEP_SHADOW_INTEGRATE_OPERATOR_WORKFLOW", "TIGHTEN_CAPS_OR_RANKING_HANDOFF",
             "REFINE_COMPLETION_LAYER", "REFINE_BC_RANKING", "ROLLBACK_OR_RESEARCH_ONLY")
TRIAL_VERDICTS = ("A — SHADOW_TRIAL_PASS", "B — SHADOW_TRIAL_MIXED", "C — SHADOW_TRIAL_FAIL")
CONTESTS = ("loopfi", "basin", "bakerfi", "plaza", "concrete", "notional", "reserve",
            "astaria", "ethos", "hybra", "sentiment", "benddao", "monetrix")
# Frozen module/config hashes — must be unchanged (no tuning during the trial).
FROZEN = {
    "scripts/research/recall_first_harness.py": "be428a1202c45b1a",
    "config/research_recall_first_harness.json": "0ea77ea476450520",
    "scripts/research/recall_first_shape_sweep.py": "a48336275cb65a4f",
    "config/research_recall_first_shape_sweep.json": "62e860199e7c51cd",
    "scripts/research/locus_shape_prioritizer.py": "d6b494bc3c0cc746",
    "config/research_locus_shape_prioritizer.json": "c61da091ad3ed21e",
}
FORBIDDEN = {
    "scripts/dashboard_sync.py": "c1af70e1",
    "prompts/deep_trace.md": "c095c426",
    "scripts/min_confirm_gate.py": "2a15169a",
    "scripts/confirm_gate.py": "afc481c9",
    "scripts/validate_p208_l3_readiness.py": "ae55eb80",
}
PROMO_FALSE = ("reportable", "submission_ready", "concluded", "emits_finding", "production_routing")


def _sha16(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def test_docs_exist_and_recognized_verdict():
    for d in DOCS:
        assert (BASE / d).exists(), f"missing {d}"
    v = (BASE / "VERDICT.md").read_text()
    assert any(x in v for x in TRIAL_VERDICTS)
    assert any(x in v for x in DECISIONS)


def test_frozen_modules_not_tuned():
    for rel, h in FROZEN.items():
        assert _sha16(ROOT / rel) == h, f"{rel} changed during the trial (tuning forbidden)"


def test_forbidden_files_byte_identical():
    for rel, h in FORBIDDEN.items():
        assert _sha16(ROOT / rel).startswith(h), f"forbidden file {rel} changed"


def test_all_13_outputs_guard_pass_and_zero_fp():
    for c in CONTESTS:
        gd = json.loads((OUT / c / "recall_guard_report.json").read_text())
        md = json.loads((OUT / c / "recall_metrics.json").read_text())
        assert gd["result"] == "PASS", f"{c} guard not PASS"
        assert gd["guard_violations"] == 0 and md["guard_violations"] == 0, f"{c} has FP/violations"


def test_every_advisory_candidate_unpromoted():
    for c in CONTESTS:
        ad = json.loads((OUT / c / "recall_advisory_candidates.json").read_text())
        assert ad["emits_findings"] is False and ad["concludes_vulnerability"] is False
        for cand in ad["advisory_candidates"]:
            assert cand["severity"] is None
            assert cand["status"] == "ADVISORY_RECALL_CANDIDATE"
            for f in PROMO_FALSE:
                assert cand[f] is False, f"{c} candidate has {f} set"


def test_aggregate_metrics_present_and_consistent():
    agg = json.loads((OUT / "p265_aggregate_metrics.json").read_text())
    assert agg["trial_contests"] == 13
    assert agg["frozen_inputs_identical_across_runs"] is True
    p = agg["pooled"]
    assert p["concluded_reportable_FP_total"] == 0 and p["guard_all_pass"] is True
    assert p["advisory_candidates_total"] == sum(r["advisory_candidates"] for r in agg["per_contest"])
    assert p["recall_delta_total"] + p["narrow_baseline_total"] == p["advisory_candidates_total"]
    assert 0.0 <= p["recall_delta_fraction_pooled"] <= 1.0
    # exactly one clean scored anchor (benddao)
    anchors = [r for r in agg["per_contest"] if r["scored_status"] == "clean_public_anchor"]
    assert len(anchors) == 1 and anchors[0]["contest"] == "benddao"
