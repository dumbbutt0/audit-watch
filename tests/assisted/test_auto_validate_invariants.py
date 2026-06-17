"""P101: autonomous validation loop — RESEARCH-ONLY, un-wired.

Proves the loop enumerates -> defense-maps -> validates -> ranks WITHOUT human invariant selection, with the
three-layer output (generated / validated / human-actionable), strict precision gates, and no submission path.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "assisted"))
import auto_validate_invariants as A  # noqa: E402
import validate_candidate_invariant as V  # noqa: E402
import funnel  # noqa: E402

GOOD_TRACE = {"localized_mechanism": "sellLimit", "controlled_inputs": "self-buy cycles",
              "pre_state": "bought/sold/total", "operation_trace": "bought inflates sellLimit",
              "boundary_cases": "k cycles exceed cap", "post_state": "cap defeated", "concrete_outcome": "PASS"}
GOOD_IMPACT = {"impact_class": "medium", "proven_magnitude": "significant", "source_true": True,
               "source_backed": True, "material_consequence": ["denial_of_asset_movement"]}


def _m11_ord(inv_stmt):
    return {"relied_upon_invariant": inv_stmt, "mechanism_class": "accounting", "counterexample_found": True,
            "counterexample_trace": "self-purchase inflates bought -> sellLimit grows beyond cap"}


def _m11():
    inv_stmt = "a holder cannot list/sell more than maxSellPercent of their original allocation"
    return A.auto_validate({
        "subject": "secondswap-2024-12", "contract": "SecondSwap_VestingManager", "function": "listVesting",
        "state_variables": ["bought", "sold", "maxSellPercent"],
        "source_text": "sellLimit = bought + maxSellPercent*(currentAlloc+sold-bought)/BASE; require(sold<=sellLimit)",
        "affected_actor": "issuer/honest market", "trigger_actor": "self-purchasing holder",
        "evidence_by_type": {"cap_limit": {"depth_trace": GOOD_TRACE, "adversarial_ordering": _m11_ord(inv_stmt),
                                           "impact_assessment": GOOD_IMPACT,
                                           "rank_signals": {"exploitability": True, "consequence": True}}},
    })


def test_self_test_passes():
    assert A._self_test() == 0


def test_three_layers_present():
    r = _m11()
    assert "generated_invariants" in r and "validated_candidates" in r and "human_actionable_candidates" in r
    assert r["counts"]["generated"] >= 4


def test_validates_without_human_selection():
    r = _m11()
    val = {x["invariant_type"] for x in r["validated_candidates"]}
    assert "cap_limit" in val  # the loop picked it among many, no human selected


def test_token_sum_not_the_only_path():
    r = _m11()
    gen = {i["invariant_type"] for i in r["generated_invariants"]}
    assert "per_user_accounting" in gen and "cap_limit" in gen and gen != {"value_conservation"}


def test_generated_stay_hypothesis_only():
    r = _m11()
    assert all(i["status"] == "HYPOTHESIS_ONLY" for i in r["generated_invariants"])
    # nothing in the output is a finding / submission
    blob = json.dumps(r).upper()
    assert '"SUBMITTED"' not in blob and "SUBMISSION_READY" not in blob


def test_defense_covers_blocks_correct_invariant():
    """A correctly-generated invariant whose defense COVERS (no bypass) is REJECTED — recall doesn't bypass defenses."""
    r = A.auto_validate({
        "contract": "SecondSwap_Marketplace", "function": "spotPurchase",
        "source_text": 'require(msg.sender != listing.seller, "no self purchase");',
        "affected_actor": "holder", "trigger_actor": "self-buyer",
        "evidence_by_type": {"role_access": {"depth_trace": GOOD_TRACE, "impact_assessment": GOOD_IMPACT}},
    })
    role = [x for x in r["rejected"] if x["invariant_type"] == "role_access"]
    assert role and role[0]["decision"] == A.REJECTED_DEFENSE_COVERS


def test_evidence_less_hypotheses_stall_not_promote():
    r = _m11()
    # the non-cap_limit hypotheses have no evidence -> NEEDS_CONTEXT, never validated
    assert r["counts"]["needs_context"] >= 1
    assert all(x["invariant_type"] != "value_conservation" for x in r["validated_candidates"])


def test_only_poc_ready_surfaced():
    r = _m11()
    for x in r["human_actionable_candidates"]:
        if x["decision"] == V.NEEDS_EXECUTION:
            assert x.get("execution_test_idea")
        else:
            assert x["decision"] == V.VALIDATED


def test_hypothesis_cannot_enter_funnel_as_handoff():
    """A bare enumerated hypothesis, dropped into a funnel record, cannot reach POC_HANDOFF_STARTED."""
    import enumerate_candidate_invariants as E
    inv = E.enumerate_invariants({"contract": "C", "function": "f", "source_snippet": "x"})["candidate_invariants"][0]
    rec = {"record_id": "hyp:1", "subject": "x", "finding_id": "HYP", "contract": "C", "function": "f",
           "conversion": "NONE", "severity_gate": "n/a", "adversarial_result": "n/a",
           "safety": {"source_false": False, "unsupported_ready": False, "hard_fail": False},
           "candidate_invariant": inv["invariant_statement"]}
    ok, reasons = funnel.can_promote_to_poc_handoff(rec)
    assert not ok  # a hypothesis is not a finding
    assert funnel.compute_pipeline_status(rec) != "POC_HANDOFF_STARTED"


def test_no_auto_submission_path():
    import inspect
    src = inspect.getsource(A)
    assert "requests" not in src and "http" not in src.lower().replace("https://json", "")  # no network/submit


# ----------------------------------------- P103 subject-level coverage (run_subject)
def _vault_dir(tmp_path):
    (tmp_path / "Vault.sol").write_text("""
contract Vault {
    uint256 public total;
    constructor(uint256 t) { total = t; }
    function deposit(uint256 a) external { total += a; }
    function withdraw(uint256 a) public { total -= a; }
    function _internalOnly() internal { total++; }
}
""")
    return tmp_path


def test_run_subject_covers_inventory_only_functions(tmp_path):
    rs = A.run_subject(_vault_dir(tmp_path), lens_leads=[], subject="unit")
    assert "Vault.deposit" in rs["enumerated_functions"]
    assert "Vault.withdraw" in rs["enumerated_functions"]
    assert "Vault._internalOnly" in rs["skipped_functions"]


def test_run_subject_constructors_isolated(tmp_path):
    rs = A.run_subject(_vault_dir(tmp_path), subject="unit")
    assert any(c["contract"] == "Vault" for c in rs["constructor_candidates"])
    assert all(hc["function"] != "constructor" for hc in rs["human_actionable_candidates"])


def test_run_subject_no_evidence_no_promotion(tmp_path):
    rs = A.run_subject(_vault_dir(tmp_path), subject="unit")  # no evidence
    assert rs["counts"]["generated"] >= 8           # recall expands
    assert rs["counts"]["validated_for_poc"] == 0   # precision holds
    assert rs["counts"]["human_actionable"] == 0
    assert rs["counts"]["false_promotions"] == 0


def test_run_subject_evidence_validates_via_same_gates(tmp_path):
    ev = {("Vault", "withdraw"): {"value_conservation": {
        "depth_trace": {"localized_mechanism": "withdraw underflow", "controlled_inputs": "a>total",
                        "pre_state": "total", "operation_trace": "total-=a underflows", "boundary_cases": "a>total",
                        "post_state": "underflow", "concrete_outcome": "PASS"},
        "adversarial_ordering": {"relied_upon_invariant": "total never negative", "mechanism_class": "accounting",
                                 "counterexample_found": True, "counterexample_trace": "withdraw>total"},
        "impact_assessment": {"impact_class": "medium", "proven_magnitude": "significant", "source_true": True,
                              "source_backed": True, "material_consequence": ["loss_of_capital"]}}}}
    rs = A.run_subject(_vault_dir(tmp_path), evidence_by_fn=ev, subject="unit")
    val = {(r["function"], r["invariant_type"]) for r in rs["validated_candidates"]}
    assert ("withdraw", "value_conservation") in val
    assert rs["counts"]["validated_for_poc"] == 1  # only the evidenced one; no decoy explosion


def test_run_subject_hypothesis_only_and_no_submission(tmp_path):
    rs = A.run_subject(_vault_dir(tmp_path), subject="unit")
    assert all(i["status"] == "HYPOTHESIS_ONLY" for i in rs["generated_invariants"])
    blob = json.dumps(rs).upper()
    assert '"SUBMITTED"' not in blob and "SUBMISSION_READY" not in blob
