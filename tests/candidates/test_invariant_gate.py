"""Gate 5 (invariant) tests — real validateBorrowATokenIncreaseLteDebtTokenDecrease analysis, no bug claim."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "candidates"))
from gates import reachability_gate, context_map_gate, defense_map_gate, invariant_gate  # noqa: E402

TARGET = "audits/size-credit-2024-06/contracts/2024-06-size"
MULTICALL = "audits/size-credit-2024-06/contracts/2024-06-size/contracts/libraries/Multicall.sol"
SIZE = "audits/size-credit-2024-06/contracts/2024-06-size/contracts/Size.sol"


def _through_defense():
    cand = {"detector": "multicall_invariant", "contract": "Multicall", "function": "multicall",
            "candidate_surface": "Multicall.multicall", "file": MULTICALL, "line": 26, "visibility": "internal",
            "code_snippet": "borrowATokenSupplyBefore debtTokenSupplyBefore borrowATokenSupplyAfter debtTokenSupplyAfter"}
    reach, _ = reachability_gate.run(cand, TARGET)
    cs, sm, _ = context_map_gate.run(cand, TARGET, facade_files=[SIZE])
    defense, _ = defense_map_gate.run(cand, TARGET, reach, cs, sm)
    return cand, sm, defense


def test_invariant_extracts_final_validation():
    cand, sm, defense = _through_defense()
    body, state = invariant_gate.run(cand, TARGET, sm, defense)
    assert state == "INVARIANT_ANALYZED"
    assert body["final_validation_function"] == "validateBorrowATokenIncreaseLteDebtTokenDecrease"
    assert body["final_validation_location"].endswith("CapsLibrary.sol:19")
    assert "revert" in body["final_validation_code_excerpt"]
    assert "borrowATokenCap" in body["final_validation_code_excerpt"]


def test_invariant_records_before_after_state():
    cand, sm, defense = _through_defense()
    body, _ = invariant_gate.run(cand, TARGET, sm, defense)
    pre = " ".join(body["pre_state_variables"]).lower()
    post = " ".join(body["post_state_variables"]).lower()
    assert "before" in pre and "after" in post
    assert "balanceof(address(this))" in pre and "totalsupply" in pre


def test_invariant_coverage_conclusion_and_skipped():
    cand, sm, defense = _through_defense()
    body, _ = invariant_gate.run(cand, TARGET, sm, defense)
    assert body["coverage_analysis"]
    cov = body["coverage_analysis"][0]["coverage_status"]
    assert cov in ("partially_covers / cannot_determine", "partially_covers", "cannot_determine", "appears_incomplete")
    assert any(s["name"] == "validateBorrowATokenCap" for s in body["skipped_or_deferred_checks"])
    assert body["accounting_basis_analysis"]["same_basis"] is False


def test_invariant_does_not_claim_a_bug():
    cand, sm, defense = _through_defense()
    body, _ = invariant_gate.run(cand, TARGET, sm, defense)
    assert "HYPOTHESIS" in body["candidate_risk_statement"]
    blob = json.dumps(body).lower()
    for positive in ("confirmed bug", "proven exploit", "is exploitable", "confirmed vulnerability", "proven bypass"):
        assert positive not in blob
    assert body["next_required_gate"] == "sequence_gate"
    # alias keys for dashboard present
    for k in ("invariant_statement", "covers", "may_not_cover", "sufficient_or_incomplete", "security_property"):
        assert k in body
