"""P259 — award-class-fit discovery confirmation. Docs guard (no pipeline behavior)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "documentation/research/assisted_mode/p259_award_class_fit_discovery"
CONTESTS = ("hybra", "sentiment")
PER_CONTEST = ("BASE_FREEZE_", "SELECTED_LOCI_", "MECHANISM_DISCOVERY_", "DISCOVERY_COVERAGE_",
               "RANKING_ABLATION_", "PROCEDURE_OUTPUTS_", "REVEAL_AND_SCORE_")
TOP_DOCS = ("TARGET_FIT_SCREEN.md", "SETUP.md", "P259_DIAGNOSIS.md", "VERDICT.md")
BOTTLENECKS = ("TARGET_FIT_GAP", "LOCUS_SELECTION_GAP", "MECHANISM_DISCOVERY_GAP", "MECHANISM_RANKING_GAP",
               "CHAIN_COMPLETION_GAP", "COMBINED_DISCOVERY_PLUS_RANKING_GAP", "PROCEDURE_READY_FOR_HARNESS",
               "PROCEDURE_NOT_USEFUL")
VERDICTS = ("BUILD_DISCOVERY_HARNESS", "BUILD_RANKING_HARNESS_PROFILE_B", "BUILD_RANKING_HARNESS_PROFILE_C",
            "BUILD_DISCOVERY_PLUS_TOP2_RANKING_HARNESS", "NEEDS_MORE_HELDOUT", "STOP_NOT_USEFUL")
OPS = ("STATE_TRANSITION_SIMULATION", "ADVERSARIAL_ACTOR_SUBSTITUTION", "TERMINAL_STATE_EVALUATION",
       "INVARIANT_DELTA_COMPUTATION", "CROSS_CALL_IDENTITY_TRACKING")
PROFILES = ("Profile A", "Profile B", "Profile C")
FAMILIES = ("accounting", "convexity", "state-machine", "reentrancy", "migration", "identity", "temporal")
TEMPLATES = ("external-dependency", "redemption/withdrawal", "reentrancy-through", "migration/conversion-residue",
             "state-machine-liveness", "cross-transaction", "liquidation/solvency", "share-price/donation/inflation")
IN_LOCUS_CLASSES = ("NOT_ENUMERATED", "ENUMERATED_OUTSIDE_TOP5", "ENUMERATED_TOP5_BUT_NOT_TOP2",
                    "ENUMERATED_TOP2_BUT_RANKED_TOO_LOW", "SELECTED_BUT_NOT_COMPLETED", "COMPLETED_CORRECTLY")
OUTSIDE_CLASSES = ("OUTSIDE_SELECTED_LOCUS_BASE_MISSED", "OUTSIDE_SELECTED_LOCUS_CHECKPOINT_MISSED",
                   "OUTSIDE_SELECTED_LOCUS_NOT_IN_SCOPE_FOR_THIS_PHASE")
AWARD_CLASSES = ("subtle_accounting_state", "external_dependency_dos", "reentrancy_state", "migration_conversion",
                 "mechanical_math_typo", "access_control", "token_compatibility", "other")


def test_all_docs_exist():
    for d in TOP_DOCS:
        assert (BASE / d).exists(), f"missing {d}"
    for c in CONTESTS:
        for pre in PER_CONTEST:
            assert (BASE / f"{pre}{c}.md").exists(), f"missing {pre}{c}.md"


def test_bottleneck_and_verdict_recognized():
    v = (BASE / "VERDICT.md").read_text()
    assert any(b in v for b in BOTTLENECKS) and any(x in v for x in VERDICTS)


def test_target_fit_screen_and_precheck():
    scr = (BASE / "TARGET_FIT_SCREEN.md").read_text()
    assert "SELECT" in scr and "REJECT" in scr and "CONTAMINATED" in scr
    setup = (BASE / "SETUP.md").read_text()
    assert "REVEAL_AVAILABILITY_PRECHECK" in setup and "content-safe" in setup.lower()


def test_two_pass_discovery_present():
    for c in CONTESTS:
        disc = (BASE / f"MECHANISM_DISCOVERY_{c}.md").read_text()
        assert "Pass 1" in disc and "Pass 2" in disc


def test_ops_profiles_families_templates():
    setup = (BASE / "SETUP.md").read_text().lower()
    for op in OPS:
        assert op in (BASE / "SETUP.md").read_text(), f"op {op} missing"
    for fam in FAMILIES:
        assert fam in setup, f"family {fam} missing"
    for t in TEMPLATES:
        assert t in setup, f"template {t} missing"
    for c in CONTESTS:
        abl = (BASE / f"RANKING_ABLATION_{c}.md").read_text()
        for p in PROFILES:
            assert p in abl, f"{p} missing in {c} ablation"


def test_all_scoring_classes_present():
    blob = (BASE / "P259_DIAGNOSIS.md").read_text()
    for c in CONTESTS:
        blob += (BASE / f"REVEAL_AND_SCORE_{c}.md").read_text()
    blob += (BASE / "SETUP.md").read_text()
    for cls in IN_LOCUS_CLASSES + OUTSIDE_CLASSES + AWARD_CLASSES:
        assert cls in blob, f"scoring class missing: {cls}"


def test_freeze_hashes_echoed():
    for c, hashes in (
        ("hybra", ("ad80d9df2f477303", "971844b6db384b04", "09693336836aff5d",
                   "ba6ca44fe91fe9c0", "fe12b727e2d4ee70", "f24ca7d30c02604e")),
        ("sentiment", ("b6494e085ac6de0b", "f1b13eb5ed609dcd", "909f931d6df2dad5",
                       "5d3adefe6d4968bf", "b3bccb5ef3ec9758", "ccdc0ea70306fc7b")),
    ):
        rev = (BASE / f"REVEAL_AND_SCORE_{c}.md").read_text()
        for h in hashes:
            assert h in rev, f"{c} missing freeze hash {h}"


def test_checkpoint_outputs_zero_conclusions():
    outs = list((BASE / "outputs").glob("*_checkpoint.json"))
    assert len(outs) >= 4
    for f in outs:
        d = json.loads(f.read_text())
        assert d["emits_findings"] is False and d["concludes_vulnerability"] is False
        assert all(r.get("severity") is None and r.get("concluded") is False for r in d["records"])
