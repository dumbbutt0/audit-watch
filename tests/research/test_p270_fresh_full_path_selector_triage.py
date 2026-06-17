"""P270 — fresh full-path rerun with selector + impact-first triage. Guard test (research-only, advisory)."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "documentation/research/assisted_mode/p270_fresh_full_path_selector_triage"
OUT = BASE / "outputs"
DOCS = ("TARGET_SCREEN.md", "SETUP.md", "BASE_AND_HARNESS_FREEZE.md", "DASHBOARD_SURFACE.md", "SELECTOR_OUTPUTS.md",
        "IMPACT_FIRST_TRIAGE.md", "RANKING_AND_COMPLETION.md", "POC_INTENT.md", "POC_RESULTS.md",
        "PRE_REVEAL_GATE.md", "REVEAL_AND_SCORE.md", "P270_DIAGNOSIS.md", "VERDICT.md", "ROLLBACK_PLAN.md")
BOTTLENECKS = ("TARGET_FIT_GAP", "RECALL_GAP", "SELECTOR_GAP", "TRIAGE_GAP", "COMPLETION_GAP", "POC_HARNESS_GAP",
               "GATE_GAP", "FULL_PATH_VALIDATED", "INCONCLUSIVE")
VERDICTS = ("FULL_PATH_READY_FOR_REPEAT_SHADOW_ROLLOUT", "EXACT_RECOVERY_PROVEN_NEEDS_MORE_REPLICATION",
            "STRONG_PARTIAL_ONLY_NEEDS_COMPLETION_REFINEMENT", "STILL_SELECTING_NONAWARDED_TRUE_POSITIVES",
            "NEEDS_MORE_FRESH_PROOF", "STOP_NOT_USEFUL", "ABORTED_SAFETY_OR_CONTAMINATION")
PROMO_FALSE = ("reportable", "submission_ready", "concluded", "emits_finding", "production_routing")
SELECTOR_SELECT = ("SELECT_FOR_FULL_POC", "SELECT_FOR_PARTIAL_RUNTIME", "SELECT_FOR_MANUAL_HARNESS_DESIGN")
FROZEN = {
    "scripts/research/locus_shape_prioritizer.py": "d6b494bc3c0cc746",
    "scripts/research/recall_first_shape_sweep.py": "a48336275cb65a4f",
    "scripts/research/recall_first_harness.py": "be428a1202c45b1a",
    "scripts/research/mechanism_pairwise_selector.py": "b0623b8c88752059",
    "scripts/research/impact_first_poc_triage.py": "63c88d02d2c7eefa",
}
FORBIDDEN = {
    "scripts/dashboard_sync.py": "c1af70e1", "prompts/deep_trace.md": "c095c426",
    "scripts/min_confirm_gate.py": "2a15169a", "scripts/confirm_gate.py": "afc481c9",
    "scripts/validate_p208_l3_readiness.py": "ae55eb80",
}


def _sha16(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def test_docs_and_recognized_bottleneck_verdict():
    for d in DOCS:
        assert (BASE / d).exists(), f"missing {d}"
    v = (BASE / "VERDICT.md").read_text()
    assert any(b in v for b in BOTTLENECKS) and any(x in v for x in VERDICTS)


def test_advisory_feed_advisory_only():
    feed = json.loads((OUT / "advisory_recall_feed.json").read_text())
    assert feed["is_gate"] is False and feed["emits_findings"] is False
    for ctrl in ("promote_to_finding", "confirm", "set_severity", "mark_reportable", "mark_submission_ready", "submit"):
        assert ctrl in feed["controls_absent"]
    for c in feed["advisory_candidates"]:
        assert c["status"] == "ADVISORY_RECALL_CANDIDATE" and c["severity"] is None
        for f in PROMO_FALSE:
            assert c[f] is False


def test_selector_outputs_consumed_by_triage():
    """Selector decisions exist (advisory) and the triage input carries selector_outcome -> consumed downstream."""
    sel = json.loads((OUT / "p270_selector_decisions.json").read_text())
    assert sel["emits_findings"] is False
    for d in sel["decisions"]:
        assert d["status"] == "ADVISORY_SELECTOR_DECISION" and d["severity"] is None
    tri_in = json.loads((OUT / "p270_triage_input.json").read_text())
    assert any("selector_outcome" in c for c in tri_in["candidates"]), "triage did not consume selector outputs"


def test_triage_routes_high_impact_heavy_not_descoped():
    """The P270-critical assertion: the heavy award-class subsystems are SELECTED (PARTIAL_RUNTIME), not de-scoped;
    the unsupported high-drama candidate is NOT selected."""
    tri = json.loads((OUT / "p270_triage_decisions.json").read_text())
    d = {x["id"]: x for x in tri["decisions"]}
    for high in ("wc_liq_misalloc", "fm_baddebt_acct"):
        assert d[high]["outcome"] in SELECTOR_SELECT, f"{high} de-scoped"
        assert d[high]["heavy_poc"] is True, f"{high} should be routed heavy"
    assert d["nft_mint_drama"]["outcome"] not in SELECTOR_SELECT, "routed unsupported drama"
    for x in tri["decisions"]:
        assert x["status"] == "ADVISORY_TRIAGE_DECISION" and x["severity"] is None
        for f in PROMO_FALSE:
            assert x[f] is False


def test_no_severe_concluded_reportable_fp():
    rev = (BASE / "REVEAL_AND_SCORE.md").read_text()
    assert "FALSE_POSITIVE (severe concluded/reportable): 0" in rev


def test_reveal_presupposes_frozen_prereveal_set():
    rev = (BASE / "REVEAL_AND_SCORE.md").read_text()
    for h in ("85456aa9241c1728", "fb02f1dfeac93c0b", "a959817f13baabca"):  # selector / poc_intent / poc
        assert h in rev, f"freeze hash {h} missing from reveal doc"


def test_frozen_modules_not_tuned():
    for rel, h in FROZEN.items():
        assert _sha16(ROOT / rel) == h, f"{rel} changed during P270 (no tuning allowed)"


def test_forbidden_files_byte_identical():
    for rel, h in FORBIDDEN.items():
        assert _sha16(ROOT / rel).startswith(h), f"forbidden file {rel} changed"


def test_poc_isolated_under_p270():
    assert (ROOT / "pocs/p270/wise/foundry.toml").exists()
    assert (ROOT / "pocs/p270/wise/test/P270_PendleShare.t.sol").exists()
