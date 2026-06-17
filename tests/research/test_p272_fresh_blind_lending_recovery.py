"""P272 — fresh blind lending recovery (full chain + P271 checklist). Guard test (research-only, advisory)."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "documentation/research/assisted_mode/p272_fresh_blind_lending_recovery"
OUT = BASE / "outputs"
DOCS = ("TARGET_SCREEN.md", "SETUP.md", "BASE_AND_HARNESS_FREEZE.md", "DASHBOARD_SURFACE.md", "SELECTOR_OUTPUTS.md",
        "IMPACT_FIRST_TRIAGE.md", "RANKING_AND_COMPLETION.md", "POC_INTENT.md", "POC_RESULTS.md", "PRE_REVEAL_GATE.md",
        "REVEAL_AND_SCORE.md", "P272_DIAGNOSIS.md", "VERDICT.md", "ROLLBACK_PLAN.md")
BOTTLENECKS = ("AWARD_CLASS_TARGET_FIT", "RECALL", "SELECTOR", "TRIAGE", "COMPLETION", "POC_HARNESS", "GATE",
               "TARGET_FIT", "FULL_PATH_VALIDATED", "INCONCLUSIVE", "objective mismatch")
VERDICTS = ("EXACT_OR_STRONG_RECOVERED_WITH_RUNTIME", "RIGHT_LOCI_FAMILY_AGAIN_EXACT_STILL_PARTIAL",
            "MISSES_AWARDED_LOCI", "PROVES_NONAWARDED_TRUE_POSITIVES", "NEEDS_MORE_FRESH_PROOF",
            "ABORTED_SAFETY_OR_CONTAMINATION")
PROMO_FALSE = ("reportable", "submission_ready", "concluded", "emits_finding", "production_routing")
SELECT = ("SELECT_FOR_FULL_POC", "SELECT_FOR_PARTIAL_RUNTIME", "SELECT_FOR_MANUAL_HARNESS_DESIGN")
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
    for c in feed["advisory_candidates"]:
        assert c["status"] == "ADVISORY_RECALL_CANDIDATE" and c["severity"] is None
        for f in PROMO_FALSE:
            assert c[f] is False


def test_selector_consumed_by_triage_and_high_impact_routed():
    tin = json.loads((OUT / "p272_triage_input.json").read_text())
    assert any("selector_outcome" in c for c in tin["candidates"]), "triage did not consume selector outputs"
    tri = json.loads((OUT / "p272_triage_decisions.json").read_text())
    d = {x["id"]: x for x in tri["decisions"]}
    # at least one high-impact lending candidate routed; unsupported drama not routed
    assert any(d[k]["outcome"] in SELECT for k in d), "no candidate routed"
    assert d["harvest_drama"]["outcome"] not in SELECT
    for x in tri["decisions"]:
        assert x["status"] == "ADVISORY_TRIAGE_DECISION" and x["severity"] is None


def test_completion_references_p271_checklist():
    rc = (BASE / "RANKING_AND_COMPLETION.md").read_text()
    assert "LENDING_COMPLETION_CHECKLIST" in rc or "checklist" in rc.lower()


def test_no_severe_concluded_reportable_fp():
    assert "FALSE_POSITIVE (severe concluded/reportable): 0" in (BASE / "REVEAL_AND_SCORE.md").read_text()


def test_reveal_presupposes_frozen_prereveal_set():
    rev = (BASE / "REVEAL_AND_SCORE.md").read_text()
    for h in ("2c5ac56b6605ca6e", "e9cbb1a2a4ac8b18", "6b4f5189e43d03bd"):  # completion / poc_intent / poc
        assert h in rev, f"freeze hash {h} missing from reveal doc"


def test_frozen_modules_not_tuned():
    for rel, h in FROZEN.items():
        assert _sha16(ROOT / rel) == h, f"{rel} changed during P272 (no tuning allowed)"


def test_forbidden_files_byte_identical():
    for rel, h in FORBIDDEN.items():
        assert _sha16(ROOT / rel).startswith(h), f"forbidden file {rel} changed"


def test_poc_isolated_under_p272():
    assert (ROOT / "pocs/p272/init/foundry.toml").exists()
    assert (ROOT / "pocs/p272/init/test/C_LiqIncentiveCapOrdering.t.sol").exists()
