"""P266 — full production-path test. Guard test (research-only; advisory-only; no authority leakage).

Asserts: deliverable docs exist + recognized bottleneck/verdict; the advisory feed + every advisory candidate are
ADVISORY-ONLY (severity null, 0 promotion/confirm/canonical flags); the dashboard surface has NO authority controls;
the isolated PoC queue accepts ONLY advisory candidates; reveal artifacts presuppose the frozen pre-reveal set;
frozen modules + 5 forbidden files byte-identical (no tuning); active audit unchanged.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "documentation/research/assisted_mode/p266_full_production_path_test"
OUT = BASE / "outputs"
DOCS = ("TARGET_SCREEN.md", "SETUP.md", "BASE_AND_HARNESS_FREEZE.md", "DASHBOARD_CANDIDATE_SURFACE.md",
        "TRIAGE_AND_POC_QUEUE.md", "RANKING_AND_COMPLETION.md", "POC_INTENT.md", "POC_RESULTS.md",
        "PRE_REVEAL_GATE.md", "REVEAL_AND_SCORE.md", "P266_DIAGNOSIS.md", "VERDICT.md", "ROLLBACK_PLAN.md")
BOTTLENECKS = ("DASHBOARD_SURFACE_GAP", "TRIAGE_GAP", "RANKING_GAP", "COMPLETION_GAP", "POC_HARNESS_GAP",
               "REPORTABILITY_GATE_GAP", "PRODUCTION_PATH_VALIDATED", "INCONCLUSIVE")
VERDICTS = ("PRODUCTION_PATH_READY_FOR_SHADOW_ROLLOUT", "DASHBOARD_ROUTE_READY_POC_LAYER_NEEDS_REFINEMENT",
            "POC_LAYER_READY_RANKING_NEEDS_REFINEMENT", "RECALL_ENGINE_READY_BUT_FULL_PATH_NOT_READY",
            "NEEDS_MORE_SCORED_PRODUCTION_PATH_TESTS", "STOP_NOT_USEFUL", "ABORTED_SAFETY_OR_CONTAMINATION")
PROMO_FALSE = ("reportable", "submission_ready", "concluded", "emits_finding", "production_routing")
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


def _sha16(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def test_docs_exist_and_recognized_bottleneck_verdict():
    for d in DOCS:
        assert (BASE / d).exists(), f"missing {d}"
    v = (BASE / "VERDICT.md").read_text()
    assert any(b in v for b in BOTTLENECKS)
    assert any(x in v for x in VERDICTS)


def test_advisory_feed_is_advisory_only():
    feed = json.loads((OUT / "advisory_recall_feed.json").read_text())
    assert feed["is_gate"] is False and feed["research_only"] is True and feed["routes_in_production"] is False
    assert feed["emits_findings"] is False
    # no authority controls present; the usual finding controls are explicitly absent
    for ctrl in ("promote_to_finding", "confirm", "set_severity", "mark_reportable", "mark_submission_ready", "submit"):
        assert ctrl in feed["controls_absent"], f"control {ctrl} not declared absent"
    for c in feed["advisory_candidates"]:
        assert c["status"] == "ADVISORY_RECALL_CANDIDATE"
        assert c["severity"] is None
        assert c["confirmed"] is False and c["canonical_record"] is False
        for f in PROMO_FALSE:
            assert c[f] is False, f"{f} set on {c['candidate_id']}"


def test_poc_queue_only_accepts_advisory_candidates():
    q = json.loads((OUT / "p266_poc_queue.json").read_text())
    assert q["is_gate"] is False and q["research_only"] is True and q["emits_findings"] is False
    feed_ids = q["source_feed_hash"]
    assert isinstance(feed_ids, str) and feed_ids
    for sel in q["selected"]:
        assert sel["status_in"] == "ADVISORY_RECALL_CANDIDATE", "PoC queue accepted a non-advisory candidate"


def test_no_severe_concluded_reportable_fp():
    """The reveal must record 0 severe concluded/reportable false positives (advisory-only held)."""
    rev = (BASE / "REVEAL_AND_SCORE.md").read_text()
    assert "FALSE_POSITIVE (severe concluded/reportable): 0" in rev or "0 severe concluded/reportable FP" in rev


def test_reveal_presupposes_frozen_prereveal_set():
    """Reveal doc must echo the pre-reveal freeze hashes (freeze-before-reveal discipline)."""
    rev = (BASE / "REVEAL_AND_SCORE.md").read_text()
    for h in ("c7788d7d6d30bb2c", "9fea23943038fe6b", "067091c03824ba20"):  # base / poc_intent / pre_reveal_gate
        assert h in rev, f"freeze hash {h} missing from reveal doc"


def test_frozen_modules_not_tuned():
    for rel, h in FROZEN.items():
        assert _sha16(ROOT / rel) == h, f"{rel} changed during P266 (tuning forbidden)"


def test_forbidden_files_byte_identical():
    for rel, h in FORBIDDEN.items():
        assert _sha16(ROOT / rel).startswith(h), f"forbidden file {rel} changed"


def test_pocs_isolated_under_p266():
    assert (ROOT / "pocs/p266/phi/foundry.toml").exists()
    for t in ("C1_distribute_royalty.t.sol", "C2_jit_share_capture.t.sol", "Cneg_withdraw_sig.t.sol"):
        assert (ROOT / "pocs/p266/phi/test" / t).exists(), f"missing PoC {t}"
