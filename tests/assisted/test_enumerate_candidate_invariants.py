"""P101: invariant enumeration (broad recall layer) — RESEARCH-ONLY, un-wired.

Proves the enumerator is category-complete (the historically-correct invariant is always among candidates),
that token-sum is NOT the only invariant for resale/listing flows, and that every output is HYPOTHESIS_ONLY.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "assisted"))
import enumerate_candidate_invariants as E  # noqa: E402


def _types(intake):
    return {i["invariant_type"] for i in E.enumerate_invariants(intake)["candidate_invariants"]}


def test_self_test_passes():
    assert E._self_test() == 0


def test_multiple_categories():
    t = _types({"contract": "C", "function": "f", "state_variables": ["balance", "amount"],
                "source_snippet": "transfer; require; total"})
    assert len(t) >= 4


def test_all_hypothesis_only_and_gated():
    inv = E.enumerate_invariants({"contract": "C", "function": "f", "source_snippet": "x"})["candidate_invariants"]
    assert inv and all(i["status"] == "HYPOTHESIS_ONLY" for i in inv)
    assert all(i["precision_gate_required"] and i["validation_required"]
               and i["poc_required_before_submission"] and i["human_final_gate_required"] for i in inv)


# ---- regression: each prior wrong-invariant miss must be COVERED by the candidate set ----
def test_regression_secondswap_not_only_token_sum():
    t = _types({"contract": "SecondSwap_VestingManager", "function": "listVesting",
                "state_variables": ["bought", "sold", "maxSellPercent"],
                "source_snippet": "sellLimit = bought + maxSellPercent*(currentAlloc+sold-bought)/BASE"})
    assert {"per_user_accounting", "cap_limit"} <= t          # the relevant ones
    assert t != {"value_conservation"}                        # NOT only token-sum


def test_regression_wildcat_ordering():
    t = _types({"contract": "WildcatMarket", "function": "executeWithdrawal",
                "source_snippet": "mulDiv(batch.normalizedAmountPaid, status.scaledAmount, batch.scaledTotalAmount); closed"})
    assert "ordering_race" in t and "recovery_availability" in t


def test_regression_ramses_cross_contract_exact_arith():
    invs = E.enumerate_invariants({"contract": "RamsesV3Pool", "function": "flash",
                                   "source_snippet": "paid0/feeProtocol staticcall external fee"})["candidate_invariants"]
    t = {i["invariant_type"] for i in invs}
    assert "cross_contract_consistency" in t or "reward_fee_distribution" in t


def test_regression_phi_index_and_access():
    t = _types({"contract": "Cred", "function": "_addCredIdPerAddress",
                "source_snippet": "public _add/_remove index array push role"})
    assert "index_array_integrity" in t and "role_access" in t


def test_regression_traitforge_cap():
    t = _types({"contract": "TraitForge", "function": "mintWithBudget",
                "source_snippet": "global _tokenIds vs per-gen maxTokensPerGen cap limit"})
    assert "cap_limit" in t


def test_regression_munchables_lifecycle_flag():
    t = _types({"contract": "LandManager", "function": "stakeMunchable",
                "source_snippet": "dirty flag never reset update lifecycle reward"})
    assert "lifecycle_state_transition" in t or "negative_space_missing_update" in t


def test_flags_unwired():
    assert E.FLAGS["is_gate"] is False and E.FLAGS["routes_in_production"] is False
