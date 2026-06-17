"""Phase-79 tests for the A/B/C workflow-discipline eval (RESEARCH-ONLY). Includes the ground_truth firewall."""
import copy
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from investigation import abc_eval as E  # noqa: E402


def _load():
    import json
    return json.loads(E.BATCH.read_text())["candidates"]


def test_1_ground_truth_firewall_arms_invariant():
    # arms must be invariant to ground_truth: flip a candidate's ground_truth and arm outputs must not change
    cands = _load()
    for c in cands:
        v = E.project(c)
        # firewall: projected view carries no ground_truth
        assert "ground_truth" not in v
        base = (E.arm_a(v), E.arm_b(v), E.arm_c(v))
        c2 = copy.deepcopy(c)
        c2["ground_truth"] = {"decision": "READY_FOR_HUMAN_REVIEW", "mechanism": "POISON", "reject_reason": "none"}
        v2 = E.project(c2)
        assert (E.arm_a(v2), E.arm_b(v2), E.arm_c(v2)) == base, c["candidate_id"]


def test_2_arms_reject_dict_with_ground_truth():
    import pytest
    cands = _load()
    poisoned = dict(cands[0])  # still contains ground_truth (not projected)
    for fn in (E.arm_a, E.arm_b, E.arm_c):
        with pytest.raises(AssertionError):
            fn(poisoned)


def test_3_C_safety_all_zero():
    s = E.run_batch()["safety"]["C_full"]
    assert s["unsupported_ready"] == 0 and s["source_false_promotions"] == 0
    assert s["overfit_promotions"] == 0 and s["wrong_mechanism"] == 0
    assert s["hard_fail"] == 0 and s["detector_to_finding"] == 0


def test_4_C_dominates_A_and_B_on_safety():
    s = E.run_batch()["safety"]
    def unsafe(a):
        return a["unsupported_ready"] + a["source_false_promotions"] + a["overfit_promotions"] + a["wrong_mechanism"] + a["hard_fail"]
    assert unsafe(s["C_full"]) == 0
    assert unsafe(s["C_full"]) < unsafe(s["B_defense_first"]) < unsafe(s["A_baseline"])


def test_5_baseline_falls_for_traps():
    s = E.run_batch()["safety"]["A_baseline"]
    assert s["wrong_mechanism"] >= 3   # the 3 wrong-mechanism traps
    assert s["overfit_promotions"] >= 2  # defense-present traps the baseline misses
    assert s["source_false_promotions"] >= 1  # the state-bound (falsified) trap


def test_6_defense_first_fixes_some_but_not_all():
    s = E.run_batch()["safety"]
    # B catches defense-ledger-blockable traps but still fails wrong-mechanism + falsification traps
    assert s["B_defense_first"]["overfit_promotions"] < s["A_baseline"]["overfit_promotions"]
    assert s["B_defense_first"]["wrong_mechanism"] == s["A_baseline"]["wrong_mechanism"]
    assert s["B_defense_first"]["source_false_promotions"] >= 1


def test_7_scorer_category_mapping():
    gt_rej_def = {"decision": "REJECTED", "mechanism": "missing_auth", "reject_reason": "defense"}
    gt_rej_fal = {"decision": "REJECTED", "mechanism": "signature_replay", "reject_reason": "falsified"}
    gt_poc = {"decision": "POC_REQUIRED", "mechanism": "value_flow", "reject_reason": "none"}
    assert E.score("POC_REQUIRED", "missing_auth", gt_rej_def) == "OVERFIT"
    assert E.score("POC_REQUIRED", "signature_replay", gt_rej_fal) == "SOURCE_FALSE"
    assert E.score("POC_REQUIRED", "missing_auth", gt_rej_fal) == "WRONG_MECHANISM"  # wrong mech takes precedence
    assert E.score("REJECTED", None, gt_rej_def) == "REJECT_CORRECT"
    assert E.score("POC_REQUIRED", "value_flow", gt_poc) == "STRONG_PARTIAL"
    assert E.score("READY_FOR_HUMAN_REVIEW", "value_flow", {"decision": "READY_FOR_HUMAN_REVIEW", "mechanism": "value_flow", "reject_reason": "none"}) == "CLEAN_HIT"


def test_8_hit_accrual_not_unique_to_C():
    # genuine clean leads are promoted by ALL arms -> C does not UNIQUELY accrue hits (safety win, not discovery win)
    fh = E.run_batch()["fresh_hit_candidates"]
    assert fh["A_baseline"] == fh["C_full"]  # same fresh hits across arms (the synthetic clean lead)


def test_9_no_module_or_detector_drift():
    def h(rel):
        return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()[:16]
    # P77/P78 investigation modules untouched
    assert h("scripts/investigation/deep_pass.py") == "57c29fff73803fbc"
    assert h("scripts/investigation/lead_schema.py") == "3c57f04e2f8b6332"
    assert h("scripts/investigation/transitions.py") == "2c00069cb49362e3"
    assert h("scripts/investigation/hygiene_validate.py") == "b9e18f299571f34b"
    # parked detectors + value-flow
    assert h("scripts/access_control_missing_auth_detector.py") == "f9ec0bff8de53cf0"
    assert h("scripts/access_control_wrong_actor_detector.py") == "2337edc2ded25116"
    assert h("scripts/signature_replay_nonce_detector.py") == "e72b9994100d35e7"
    assert h("scripts/value_flow_surface.py").startswith("aca9125a")
