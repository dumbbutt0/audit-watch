"""Phase-78 tests: workflow hygiene around P77 bundles (RESEARCH-ONLY). Missed verification steps fail closed."""
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from investigation.deep_pass import run, FALSIFIERS  # noqa: E402
from investigation.lead_schema import normalize_lead  # noqa: E402
from investigation.hygiene_validate import validate  # noqa: E402
from investigation.missed_step_workflow_stub import run_workflow  # noqa: E402
from investigation import transitions as T  # noqa: E402

NF = {k: False for k in FALSIFIERS}
PASS_REVIEW = {"review_status": "PASS"}
FULL_EX = {"rejection_case": "considered auth/cap/later-invariant; none block", "attacker_profile": "EOA",
           "entrypoint": "f", "preconditions": "pool funded", "transaction_sequence": "attacker calls f repeatedly",
           "state_before": "x", "state_after": "y", "broken_invariant": "conservation",
           "why_existing_defenses_do_not_block": "no cap on path", "impact_category": "fund_loss",
           "minimum_profit_or_damage_condition": "drains per call", "source_evidence": "C.sol:1-20"}


def _bundle(cid, fam, ev):
    return run(normalize_lead({"candidate_id": cid, "detector_family": fam, "contract": "C", "function": "f"}), ev)


def test_1_missing_helper_modifier_check_blocks():
    # promotion-shaped evidence but NO defense ledger (helper/modifier/library defenses never traced)
    b = _bundle("m1", "missing_auth", {"context": {"source_resolved": True}, "defense_ledger": {},
                                        "exploit": FULL_EX, "source_falsification": NF, "poc_needed": False,
                                        "critical_defenses": ["access_control"]})
    # deep_pass would NEEDS_CONTEXT (critical access_control absent); hygiene also blocks any promotion
    assert b["final_decision"] in ("NEEDS_CONTEXT", "REJECTED")
    ok, viol, rec = validate(b, PASS_REVIEW)
    assert ok and rec != "READY_FOR_HUMAN_REVIEW"  # not a promotion


def test_2_unknown_critical_defense_but_ready_fails():
    b = _bundle("m2", "signature_replay", {"context": {"source_resolved": True}, "exploit": FULL_EX, "source_falsification": NF, "poc_needed": False,
                                            "defense_ledger": {"nonce_or_replay_guard": {"classification": "bypassed"}}})
    # force the bundle to claim READY while a critical defense is unknown
    b["final_decision"] = b["status"] = "READY_FOR_HUMAN_REVIEW"
    b["defense_ledger"]["nonce_or_replay_guard"] = {"classification": "unknown"}
    ok, viol, rec = validate(b, PASS_REVIEW)
    assert not ok and any("critical defense" in x for x in viol)


def test_3_later_invariant_covers_rejected():
    b = _bundle("m3", "multicall_invariant", {"context": {"source_resolved": True},
                "defense_ledger": {"final_invariant_check": {"classification": "irrelevant"}}, "exploit": FULL_EX,
                "source_falsification": {**NF, "impact_prevented_by_later_invariant": True}, "poc_needed": True})
    assert b["final_decision"] == "REJECTED"
    wf = run_workflow(b, PASS_REVIEW)
    assert wf["final_status"] == "REJECTED" and not wf["promotion_allowed"]


def test_4_no_attacker_sequence_but_poc_required_fails():
    b = _bundle("m4", "value_flow", {"context": {"source_resolved": True}, "defense_ledger": {"accounting_invariant": {"classification": "irrelevant"}},
                                      "exploit": FULL_EX, "source_falsification": NF, "poc_needed": True})
    assert b["final_decision"] == "POC_REQUIRED"
    b["exploit_path"]["transaction_sequence"] = None  # corrupt: remove the attacker sequence
    ok, viol, rec = validate(b, PASS_REVIEW)
    assert not ok and any("transaction_sequence" in x for x in viol)


def test_5_forbidden_language_fails():
    b = _bundle("m5", "value_flow", {"context": {"source_resolved": True}, "defense_ledger": {"accounting_invariant": {"classification": "irrelevant"}},
                                      "exploit": FULL_EX, "source_falsification": NF, "poc_needed": False})
    b["human_review_notes"] = "this is a valid finding, submission ready"
    ok, viol, rec = validate(b, PASS_REVIEW)
    assert not ok and any("forbidden finality" in x for x in viol)


def test_6_detector_to_finding_direct_fails():
    b = _bundle("m6", "value_flow", {"context": {"source_resolved": True}, "defense_ledger": {"accounting_invariant": {"classification": "irrelevant"}},
                                      "exploit": FULL_EX, "source_falsification": NF, "poc_needed": False})
    b["state_trace"] = ["STATIC_LEAD", "READY_FOR_HUMAN_REVIEW"]  # the shortcut
    ok, viol, rec = validate(b, PASS_REVIEW)
    assert not ok and any("illegal state transition" in x for x in viol)
    import pytest
    with pytest.raises(T.ForbiddenTransition):
        T.assert_transition("STATIC_LEAD", "READY_FOR_HUMAN_REVIEW")


def test_7_clean_bundle_with_adversarial_pass_ready_allowed():
    b = _bundle("m7", "value_flow", {"context": {"source_resolved": True, "reachability": "external"},
                "defense_ledger": {"accounting_invariant": {"classification": "bypassed"}, "final_invariant_check": {"classification": "irrelevant"}},
                "exploit": FULL_EX, "source_falsification": NF, "poc_needed": False})
    assert b["final_decision"] == "READY_FOR_HUMAN_REVIEW"
    ok, viol, rec = validate(b, PASS_REVIEW)
    assert ok, viol
    wf = run_workflow(b, PASS_REVIEW)
    assert wf["final_status"] == "READY_FOR_HUMAN_REVIEW" and wf["promotion_allowed"]


def test_8_adversarial_unknown_blocks_promotion():
    b = _bundle("m8", "value_flow", {"context": {"source_resolved": True, "reachability": "external"},
                "defense_ledger": {"accounting_invariant": {"classification": "bypassed"}},
                "exploit": FULL_EX, "source_falsification": NF, "poc_needed": False})
    ok, viol, rec = validate(b, {"review_status": "UNKNOWN"})
    assert not ok and any("adversarial review PASS" in x for x in viol)
    wf = run_workflow(b, {"review_status": "UNKNOWN"})
    assert not wf["promotion_allowed"]


def test_9_routed_source_refused_or_failed():
    import pytest
    from investigation.lead_schema import RoutedSourceRefused
    with pytest.raises(RoutedSourceRefused):
        normalize_lead({"candidate_id": "x", "detector_family": "y", "routes_in_production": True})
    # a hand-crafted bundle that smuggles routing flags must fail hygiene
    b = _bundle("m9", "value_flow", {"context": {"source_resolved": True}, "defense_ledger": {"accounting_invariant": {"classification": "irrelevant"}},
                                      "exploit": FULL_EX, "source_falsification": NF, "poc_needed": False})
    b["routes_in_production"] = True
    ok, viol, rec = validate(b, PASS_REVIEW)
    assert not ok and any("production-routing" in x for x in viol)


def test_10_no_wiring_and_parked_artifacts_unchanged():
    for prod in ("run_pipeline.sh", "scripts/llm_runtime.py", "config/agent_policy.json", "config/runtime_policy.json"):
        p = ROOT / prod
        if p.exists():
            t = p.read_text()
            for tok in ("hygiene_validate", "missed_step_workflow", "audit-candidate-verification", "adversarial-bundle-review"):
                assert tok not in t, tok

    def h(rel):
        return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()[:16]
    assert h("scripts/access_control_missing_auth_detector.py") == "f9ec0bff8de53cf0"
    assert h("scripts/access_control_wrong_actor_detector.py") == "2337edc2ded25116"
    assert h("scripts/signature_replay_nonce_detector.py") == "e72b9994100d35e7"
    assert h("scripts/mechanism_advancement_gate.py").startswith("697e72a7")
    assert h("scripts/native_eth_sink_gate.py").startswith("5522e15f")
    assert h("scripts/value_flow_surface.py").startswith("aca9125a")
