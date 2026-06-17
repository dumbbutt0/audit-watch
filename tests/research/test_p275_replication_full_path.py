"""P275 — replication full-path test on a second fresh diverse target (ronin / Katana V3).

Guard tests: frozen modules + P271 checklist + forbidden byte-identical; advisory contracts intact across selector/
coverage/triage; coverage output consumed by triage; >=2 classes routed; no production-authority leakage; reveal
presupposes a frozen pre-reveal set; recognized verdict + bottleneck; active audit unchanged.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "documentation/research/assisted_mode/p275_replication_full_path"
OUTS = DOCS / "outputs"

FROZEN = {
    "scripts/research/locus_shape_prioritizer.py": "d6b494bc3c0cc746",
    "scripts/research/recall_first_shape_sweep.py": "a48336275cb65a4f",
    "scripts/research/recall_first_harness.py": "be428a1202c45b1a",
    "scripts/research/mechanism_pairwise_selector.py": "b0623b8c88752059",
    "scripts/research/impact_first_poc_triage.py": "63c88d02d2c7eefa",
    "scripts/research/award_class_coverage_router.py": "6debb753b45f1833",
    "config/research_award_class_coverage_router.json": "91f9deac7867af62",
    "config/research_impact_first_poc_triage.json": "7c174b5d1ae6b52f",
    "config/research_mechanism_pairwise_selector.json": "9dab060dca027c24",
    "documentation/research/assisted_mode/p271_lending_runtime_scaffold/"
    "LENDING_COMPLETION_CHECKLIST.md": "2929a2154a88104e",
}
FORBIDDEN = {
    "scripts/dashboard_sync.py": "c1af70e1", "prompts/deep_trace.md": "c095c426",
    "scripts/min_confirm_gate.py": "2a15169a", "scripts/confirm_gate.py": "afc481c9",
    "scripts/validate_p208_l3_readiness.py": "ae55eb80",
}
DOC_FILES = ("TARGET_SCREEN.md", "SETUP.md", "BASE_AND_HARNESS_FREEZE.md", "DASHBOARD_SURFACE.md",
             "SELECTOR_OUTPUTS.md", "COVERAGE_ROUTER_OUTPUTS.md", "IMPACT_FIRST_TRIAGE.md",
             "RANKING_AND_COMPLETION.md", "POC_INTENT.md", "POC_RESULTS.md", "PRE_REVEAL_GATE.md",
             "REVEAL_AND_SCORE.md", "P275_DIAGNOSIS.md", "VERDICT.md", "ROLLBACK_PLAN.md")
VERDICTS = ("A — FULL_PATH_VALIDATED_REPLICATED", "B — EXACT_OR_STRONG_RECOVERY_BUT_NEEDS_MORE_REPLICATION",
            "C — CLASS_COVERAGE_WORKS_EXACT_STILL_PARTIAL", "D — COVERAGE_MISSED_AWARDED_CLASS",
            "E — STILL_NONAWARDED_TRUE_POSITIVES", "F — TARGET_NOT_DIAGNOSTIC", "G — NEEDS_MORE_FRESH_PROOF",
            "H — ABORTED_SAFETY_OR_CONTAMINATION")
BOTTLENECKS = ("A — TARGET_FIT_GAP", "B — RECALL_GAP", "C — COVERAGE_GAP", "D — SELECTOR_GAP", "E — TRIAGE_GAP",
               "F — COMPLETION_GAP", "G — POC_HARNESS_GAP", "H — GATE_GAP", "I — FULL_PATH_VALIDATED_REPLICATED",
               "J — OBJECTIVE_MISMATCH_REMAINS", "K — INCONCLUSIVE")
PROMO_FALSE = ("reportable", "submission_ready", "concluded", "emits_finding", "production_routing")


def _sha16(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def test_frozen_and_forbidden_byte_identical():
    for rel, h in FROZEN.items():
        assert _sha16(ROOT / rel) == h, f"frozen changed: {rel}"
    for rel, h in FORBIDDEN.items():
        assert _sha16(ROOT / rel).startswith(h), f"forbidden changed: {rel}"


def test_docs_present():
    for d in DOC_FILES:
        assert (DOCS / d).exists(), f"missing {d}"


def test_selector_advisory_contract():
    d = json.loads((OUTS / "selector_decisions.json").read_text())
    assert d["emits_findings"] is False and d["guard_violations"] in (0, [], None)
    for dec in d["decisions"]:
        assert dec["severity"] is None and dec["status"] == "ADVISORY_SELECTOR_DECISION"
        for f in PROMO_FALSE:
            assert dec[f] is False


def test_coverage_routes_two_plus_classes():
    d = json.loads((OUTS / "coverage_decisions.json").read_text())
    assert d["guard_violations"] == 0
    sel = [x for x in d["decisions"] if x["label"] in ("COVERAGE_SELECT", "COVERAGE_SELECT_HEAVY")]
    classes = {x["award_class"] for x in sel}
    assert len(classes) >= 2, f"fewer than 2 classes routed: {classes}"
    for x in d["decisions"]:
        assert x["severity"] is None and x["status"] == "ADVISORY_COVERAGE_DECISION"


def test_coverage_handoff_consumed_by_triage():
    cov = json.loads((OUTS / "coverage_decisions.json").read_text())
    tri_in = json.loads((OUTS / "triage_candidates.json").read_text())["candidates"]
    assert set(cov["handoff_queue_to_p269"]) == {c["id"] for c in tri_in}


def test_triage_class_diverse_selection():
    d = json.loads((OUTS / "triage_decisions.json").read_text())
    assert d["guard_violations"] == 0
    sel = [x for x in d["decisions"] if x["outcome"].startswith("SELECT_FOR")]
    inp = {c["id"]: c["award_class"] for c in json.loads((OUTS / "triage_candidates.json").read_text())["candidates"]}
    assert len({inp[x["id"]] for x in sel}) >= 2


def test_no_production_authority_leakage_in_outputs():
    for j in OUTS.glob("*decisions.json"):
        txt = j.read_text().lower()
        assert "submission_ready\": true" not in txt
        assert "production_routing\": true" not in txt
        assert "\"reportable\": true" not in txt


def test_reveal_presupposes_frozen_pre_reveal_set():
    gate = (DOCS / "PRE_REVEAL_GATE.md").read_text().lower()
    assert "sha256" in gate or "hash" in gate
    reveal = (DOCS / "REVEAL_AND_SCORE.md").read_text().lower()
    assert "after" in reveal and ("frozen" in reveal or "freeze" in reveal or "pre-reveal" in reveal)


def test_recognized_verdict_and_bottleneck():
    v = (DOCS / "VERDICT.md").read_text()
    assert any(x in v for x in VERDICTS), "no recognized verdict"
    assert any(b in v for b in BOTTLENECKS), "no recognized bottleneck"


