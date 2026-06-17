"""Phase-77 tests for the universal candidate deep-pass (RESEARCH-ONLY, un-wired). Covers the 7 spec scenarios +
forbidden-transition + unknown-critical-defense + no-wiring/forbidden-label/routed-refusal."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from investigation.deep_pass import run, FALSIFIERS  # noqa: E402
from investigation.lead_schema import normalize_lead, RoutedSourceRefused, FLAGS  # noqa: E402
from investigation import transitions as T  # noqa: E402

NO_FALSIFIER = {k: False for k in FALSIFIERS}
FULL_EXPLOIT = {
    "rejection_case": "considered: caller attacker-controlled, no modifier on path, state mutable, no later invariant",
    "attacker_profile": "EOA, no privileged setup", "entrypoint": "f(uint256)", "preconditions": "pool funded",
    "transaction_sequence": "attacker calls f(victimId) repeatedly", "state_before": "bal[v]=100", "state_after": "bal[v]=0",
    "broken_invariant": "sum(bal) conserved", "why_existing_defenses_do_not_block": "no auth, no cap on path",
    "impact_category": "fund_loss", "minimum_profit_or_damage_condition": "drains victim balance per call",
    "source_evidence": "C.sol:40-60",
}


def _lead(cid, fam="generic"):
    return normalize_lead({"candidate_id": cid, "detector_family": fam, "contract": "C", "function": "f", "snippet": "..."})


def test_1_missing_ac_but_reachable_modifier_rejected():
    ev = {"context": {"source_resolved": True, "reachability": "external"},
          "defense_ledger": {"access_control": {"classification": "blocks_candidate", "evidence": "onlyOwner modifier on the reachable path"}}}
    r = run(_lead("ac", "missing_auth"), ev)
    assert r["final_decision"] == "REJECTED"
    assert "defense blocks" in r["status_reason"]


def test_2_missing_nonce_but_state_bound_rejected():
    # signed hash binds mutable claimed state -> source-falsified
    ev = {"context": {"source_resolved": True}, "defense_ledger": {"nonce_or_replay_guard": {"classification": "partially_covers_candidate"}},
          "exploit": FULL_EXPLOIT, "source_falsification": {**NO_FALSIFIER, "hash_or_value_bound_to_mutable_state": True}}
    r = run(_lead("nonce", "signature_replay"), ev)
    assert r["final_decision"] == "REJECTED"
    assert "hash_or_value_bound_to_mutable_state" in r["status_reason"]


def test_3_value_flow_no_defense_no_poc_required():
    ev = {"context": {"source_resolved": True}, "defense_ledger": {"final_invariant_check": {"classification": "irrelevant"}},
          "exploit": FULL_EXPLOIT, "source_falsification": NO_FALSIFIER, "poc_needed": True}
    r = run(_lead("vf", "value_flow"), ev)
    assert r["final_decision"] == "POC_REQUIRED"
    assert r["exploit_path"]["transaction_sequence"] and r["poc_needed"] is True


def test_4_multicall_final_invariant_covers_rejected():
    ev = {"context": {"source_resolved": True},
          "defense_ledger": {"final_invariant_check": {"classification": "blocks_candidate", "evidence": "final post-batch invariant re-checks the skipped per-call check"}}}
    r = run(_lead("mc", "multicall_invariant"), ev)
    assert r["final_decision"] == "REJECTED"


def test_5_missing_source_needs_context():
    ev = {"context": {"source_resolved": False, "source_available": False}}
    r = run(_lead("missing_src", "signature_replay"), ev)
    assert r["final_decision"] == "NEEDS_CONTEXT"
    assert r["missing_context"]


def test_6_strong_candidate_ready_for_human_review():
    ev = {"context": {"source_resolved": True, "reachability": "external"},
          "defense_ledger": {"access_control": {"classification": "irrelevant"}, "final_invariant_check": {"classification": "bypassed"}},
          "exploit": FULL_EXPLOIT, "source_falsification": NO_FALSIFIER, "poc_needed": False}
    r = run(_lead("strong", "value_flow"), ev)
    assert r["final_decision"] == "READY_FOR_HUMAN_REVIEW"
    assert r["invariant_analysis"]["broken_invariant"] and r["impact_analysis"]["impact_category"]
    assert all(v is False for v in r["source_falsification"].values())


def test_7_forbidden_static_to_ready_raises():
    import pytest
    with pytest.raises(T.ForbiddenTransition):
        T.assert_transition("STATIC_LEAD", "READY_FOR_HUMAN_REVIEW")
    with pytest.raises(T.ForbiddenTransition):
        T.assert_transition("STATIC_LEAD", "POC_REQUIRED")
    with pytest.raises(T.ForbiddenTransition):
        T.assert_transition("CONTEXT_MAPPED", "READY_FOR_HUMAN_REVIEW")


def test_8_unknown_critical_defense_blocks_promotion():
    ev = {"context": {"source_resolved": True}, "critical_defenses": ["external_dependency"],
          "defense_ledger": {"external_dependency": {"classification": "source_unavailable"}},
          "exploit": FULL_EXPLOIT, "source_falsification": NO_FALSIFIER, "poc_needed": False}
    r = run(_lead("unk", "oracle"), ev)
    assert r["final_decision"] == "NEEDS_CONTEXT"  # cannot promote with an unknown critical defense


def test_9_no_wiring_forbidden_labels_and_routed_refusal():
    # flags
    assert FLAGS == {"is_gate": False, "research_only": True, "review_only": True, "routes_in_production": False, "routed_manifest_ids": []}
    # routed source refused
    import pytest
    with pytest.raises(RoutedSourceRefused):
        normalize_lead({"candidate_id": "x", "detector_family": "y", "routed_manifest_ids": ["m1"]})
    # no forbidden promotion language in any emitted bundle
    bundles = [
        run(_lead("p"), {"context": {"source_resolved": True}, "defense_ledger": {"access_control": {"classification": "irrelevant"}},
                         "exploit": FULL_EXPLOIT, "source_falsification": NO_FALSIFIER, "poc_needed": False}),
        run(_lead("q"), {"context": {"source_resolved": True}, "defense_ledger": {"access_control": {"classification": "blocks_candidate", "evidence": "modifier"}}}),
    ]
    for b in bundles:
        blob = str(b).lower()
        for lab in ("confirmed bug", "valid finding", "submission ready", "submission-ready"):
            assert lab not in blob, (lab, b["final_decision"])
        assert b["status"] in ("REJECTED", "NEEDS_CONTEXT", "POC_REQUIRED", "READY_FOR_HUMAN_REVIEW")
    # no production wiring of the investigation package
    for prod in ("run_pipeline.sh", "scripts/llm_runtime.py", "config/agent_policy.json", "config/runtime_policy.json"):
        p = ROOT / prod
        if p.exists():
            assert "investigation" not in p.read_text() or "scripts/investigation" not in p.read_text()
