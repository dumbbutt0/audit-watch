"""P268 — fresh full-path test with the P267 selector. Guard test (research-only, advisory; no authority leakage).

Asserts: docs exist + recognized bottleneck/verdict; advisory feed + candidates advisory-only; selector decisions
advisory + KEEP_BOTH preserved the high-impact mechanisms; PoC queue advisory-only; reveal presupposes the frozen
pre-reveal set; frozen P260/P262/P264/P267 modules + 5 forbidden files byte-identical; active audit unchanged.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "documentation/research/assisted_mode/p268_fresh_full_path_with_selector"
OUT = BASE / "outputs"
DOCS = ("TARGET_SCREEN.md", "SETUP.md", "BASE_AND_HARNESS_FREEZE.md", "DASHBOARD_CANDIDATE_SURFACE.md",
        "TRIAGE_AND_POC_QUEUE.md", "RANKING_OUTPUTS.md", "SELECTOR_OUTPUTS.md", "COMPLETION_OUTPUTS.md",
        "POC_INTENT.md", "POC_RESULTS.md", "PRE_REVEAL_GATE.md", "REVEAL_AND_SCORE.md", "P268_DIAGNOSIS.md",
        "VERDICT.md", "ROLLBACK_PLAN.md")
BOTTLENECKS = ("TRIAGE", "RANKING", "SELECTOR", "COMPLETION", "POC", "DISCOVERY")
VERDICTS = ("FULL_PATH_SELECTOR_VALIDATED", "SELECTOR_HELPFUL_NEEDS_MORE_PROOF",
            "SELECTOR_PRESERVED_BUT_COMPLETION_FAILED", "SELECTOR_FAILED_RANKING_STILL_BLOCKS",
            "POC_LAYER_BLOCKED", "NEEDS_MORE_FRESH_TESTS", "ABORTED_CONTAMINATION_OR_SAFETY")
PROMO_FALSE = ("reportable", "submission_ready", "concluded", "emits_finding", "production_routing")
SELECTOR_OUTCOMES = ("SELECT_M1", "SELECT_M2", "KEEP_BOTH", "REFUTE_M1_FIRST", "REFUTE_M2_FIRST", "INSUFFICIENT_EVIDENCE")
FROZEN = {
    "scripts/research/locus_shape_prioritizer.py": "d6b494bc3c0cc746",
    "scripts/research/recall_first_shape_sweep.py": "a48336275cb65a4f",
    "scripts/research/recall_first_harness.py": "be428a1202c45b1a",
    "scripts/research/mechanism_pairwise_selector.py": "b0623b8c88752059",
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


def test_docs_and_recognized_bottleneck_verdict():
    for d in DOCS:
        assert (BASE / d).exists(), f"missing {d}"
    v = (BASE / "VERDICT.md").read_text()
    assert any(b in v for b in BOTTLENECKS) and any(x in v for x in VERDICTS)


def test_advisory_feed_advisory_only():
    feed = json.loads((OUT / "advisory_recall_feed.json").read_text())
    assert feed["is_gate"] is False and feed["research_only"] is True and feed["emits_findings"] is False
    for ctrl in ("promote_to_finding", "confirm", "set_severity", "mark_reportable", "mark_submission_ready", "submit"):
        assert ctrl in feed["controls_absent"]
    for c in feed["advisory_candidates"]:
        assert c["status"] == "ADVISORY_RECALL_CANDIDATE" and c["severity"] is None
        assert c["confirmed"] is False and c["canonical_record"] is False
        for f in PROMO_FALSE:
            assert c[f] is False


def test_selector_decisions_advisory_and_keep_both_preserved():
    dec = json.loads((OUT / "p268_selector_decisions.json").read_text())
    assert dec["emits_findings"] is False
    outs = {d["case"]: d for d in dec["decisions"]}
    for d in dec["decisions"]:
        assert d["severity"] is None and d["status"] == "ADVISORY_SELECTOR_DECISION"
        assert d["outcome"] in SELECTOR_OUTCOMES
        for f in PROMO_FALSE:
            assert d[f] is False
    # the two real high-vs-easy pairs must be PRESERVED (KEEP_BOTH), not dropped for the easy rival
    assert outs["C1_redeem"]["outcome"] == "KEEP_BOTH" and outs["C1_redeem"]["anti_easy_poc_flag"] is True
    assert outs["C2_mint_inflation"]["outcome"] == "KEEP_BOTH" and outs["C2_mint_inflation"]["anti_easy_poc_flag"] is True
    # the gated control is refuted, not pushed to PoC as a finding
    assert outs["Cneg_slashing"]["outcome"] == "REFUTE_M1_FIRST"


def test_poc_queue_advisory_only():
    q = json.loads((OUT / "p268_poc_queue.json").read_text())
    assert q["is_gate"] is False and q["research_only"] is True and q["emits_findings"] is False


def test_no_severe_concluded_reportable_fp():
    rev = (BASE / "REVEAL_AND_SCORE.md").read_text()
    assert "FALSE_POSITIVE (severe concluded/reportable): 0" in rev


def test_reveal_presupposes_frozen_prereveal_set():
    rev = (BASE / "REVEAL_AND_SCORE.md").read_text()
    for h in ("ad2bdc5b783f020f", "5c3ea8aac6bfbab3", "ed7fb79345dfa0be"):  # selector / gate / poc
        assert h in rev, f"freeze hash {h} missing from reveal doc"


def test_frozen_modules_not_tuned():
    for rel, h in FROZEN.items():
        assert _sha16(ROOT / rel) == h, f"{rel} changed during P268 (no tuning allowed)"


def test_forbidden_files_byte_identical():
    for rel, h in FORBIDDEN.items():
        assert _sha16(ROOT / rel).startswith(h), f"forbidden file {rel} changed"


def test_pocs_isolated_under_p268():
    assert (ROOT / "pocs/p268/karak/foundry.toml").exists()
    assert (ROOT / "pocs/p268/karak/test/P268_Vault.t.sol").exists()
