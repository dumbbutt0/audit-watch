"""P258 — widened discovery + ranking separation heldout. Docs guard (no pipeline behavior)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "documentation/research/assisted_mode/p258_widened_discovery_ranking"
CONTESTS = ("astaria", "ethos")
PER_CONTEST = ("BASE_FREEZE_", "SELECTED_LOCI_", "MECHANISM_ENUM_", "DISCOVERY_COVERAGE_",
               "RANKING_ABLATION_", "PROCEDURE_OUTPUTS_", "REVEAL_AND_SCORE_")
TOP_DOCS = ("SETUP.md", "P258_DIAGNOSIS.md", "VERDICT.md")
BOTTLENECKS = ("DISCOVERY_GAP_DOMINATES", "RANKING_GAP_DOMINATES", "COMPLETION_GAP_DOMINATES",
               "DISCOVERY_AND_RANKING_BOTH_REQUIRED", "PROCEDURE_READY_FOR_HARNESS", "PROCEDURE_NOT_USEFUL")
VERDICTS = ("BUILD_DISCOVERY_HARNESS", "BUILD_RANKING_HARNESS_PROFILE_B", "BUILD_RANKING_HARNESS_PROFILE_C",
            "BUILD_TOP2_DISCOVERY_PLUS_RANKING_HARNESS", "NEEDS_MORE_HELDOUT", "STOP_NOT_USEFUL")
OPS = ("STATE_TRANSITION_SIMULATION", "ADVERSARIAL_ACTOR_SUBSTITUTION", "TERMINAL_STATE_EVALUATION",
       "INVARIANT_DELTA_COMPUTATION", "CROSS_CALL_IDENTITY_TRACKING")
PROFILES = ("Profile A", "Profile B", "Profile C")
FAMILIES = ("ACCOUNTING", "CONVEXITY", "STATE_MACHINE", "REENTRANCY", "MIGRATION", "IDENTITY", "TEMPORAL")
AWARDED_CLASSES = ("NOT_ENUMERATED", "ENUMERATED_OUTSIDE_TOP5", "ENUMERATED_TOP5_BUT_NOT_TOP2",
                   "ENUMERATED_TOP2_BUT_RANKED_TOO_LOW", "SELECTED_BUT_NOT_COMPLETED", "COMPLETED_CORRECTLY")
PROFILE_LABELS = ("SELECTED_AWARDED", "TOP2_AWARDED", "MISRANKED_AWARDED", "MISSED_AWARDED")


def test_all_docs_exist():
    for d in TOP_DOCS:
        assert (BASE / d).exists(), f"missing {d}"
    for c in CONTESTS:
        for pre in PER_CONTEST:
            assert (BASE / f"{pre}{c}.md").exists(), f"missing {pre}{c}.md"


def test_bottleneck_and_verdict_recognized():
    v = (BASE / "VERDICT.md").read_text()
    assert any(b in v for b in BOTTLENECKS)
    assert any(x in v for x in VERDICTS)


def test_precheck_existence_only_in_setup():
    setup = (BASE / "SETUP.md").read_text()
    assert "REVEAL_AVAILABILITY_PRECHECK" in setup
    assert "no findings fetched" in setup.lower() or "content-safe" in setup.lower()


def test_five_ops_and_three_profiles():
    setup = (BASE / "SETUP.md").read_text()
    for op in OPS:
        assert op in setup, f"op {op} missing in SETUP"
    for c in CONTESTS:
        abl = (BASE / f"RANKING_ABLATION_{c}.md").read_text()
        for p in PROFILES:
            assert p in abl, f"{p} missing in {c} ablation"


def test_seven_families_present():
    setup = (BASE / "SETUP.md").read_text()
    for fam in FAMILIES:
        assert fam in setup, f"family {fam} missing in SETUP"


def test_six_awarded_classes_and_profile_labels():
    blob = (BASE / "P258_DIAGNOSIS.md").read_text()
    for c in CONTESTS:
        blob += (BASE / f"REVEAL_AND_SCORE_{c}.md").read_text()
    for cls in AWARDED_CLASSES:
        assert cls in blob, f"awarded class {cls} missing"
    for lbl in PROFILE_LABELS:
        assert lbl in blob, f"profile label {lbl} missing"


def test_freeze_hashes_echoed_in_reveal_docs():
    for c, hashes in (
        ("astaria", ("24827d902c44ea87", "435ce0d285f99671", "416b91680df93031",
                     "a7d6eb5a7697facd", "bc689dc2de3b3f8c", "b72c5a5c8458e29f")),
        ("ethos", ("9516b8f787333531", "5d097540c0627454", "38e24048df75ed18",
                   "681eeeb8631c0f2c", "d05b94eacb91305a", "3fca75e70aaac5e2")),
    ):
        rev = (BASE / f"REVEAL_AND_SCORE_{c}.md").read_text()
        for h in hashes:
            assert h in rev, f"{c} reveal missing freeze hash {h}"


def test_checkpoint_outputs_zero_conclusions():
    outs = list((BASE / "outputs").glob("*_checkpoint.json"))
    assert len(outs) >= 4, "expected 2 checkpoints x 2 contests"
    for f in outs:
        d = json.loads(f.read_text())
        assert d["emits_findings"] is False and d["concludes_vulnerability"] is False
        assert all(r.get("severity") is None and r.get("concluded") is False for r in d["records"])
