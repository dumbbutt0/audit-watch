"""P96 tests for the advisory adversarial state-ordering & boundary-enumeration check (RESEARCH-ONLY, un-wired).

This is the SECOND gate after localized_depth_trace (P92/P94): before a localized, COMPLETED REJECT may be
FINALIZED, the analyst must state the relied-upon invariant and try to break it with >=3 concrete adversarial
orderings. It repairs P95's completed-but-WRONG REJECTs (H-01 executeWithdrawal closed-market over-withdrawal;
M-05 grantRole provider-vs-provider expiry bypass) WITHOUT touching severity_impact_gate (frozen 193abf9f).
It never sets severity, never routes, never converts a REJECT into a finding — it only decides finalize vs reopen.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "investigation"))
from investigation import adversarial_ordering_check as A  # noqa: E402

REJECT_CONFIRMED = A.REJECT_CONFIRMED
REOPEN = A.REOPEN
NEEDS_EXECUTION = A.NEEDS_EXECUTION
PASS_CANDIDATE = A.PASS_CANDIDATE


def test_self_test_passes():
    assert A._self_test() == 0


# ---- regression anchor 1: P95 H-01 executeWithdrawal closed-market over-withdrawal ----

def test_anchor_p95_h01_local_pro_rata_reopens():
    case = {
        "proposed_reject_reason": "pro-rata mulDiv is correct; accounting consistent",
        "relied_upon_invariant": "sum of executed withdrawals <= batch.normalizedAmountPaid",
        "mechanism_class": "accounting",
        "ordering_cases_tested": ["open market, single withdrawal"],
        "counterexample_found": False,
    }
    assert A.evaluate(case).recommended_verdict == REOPEN


def test_anchor_p95_h01_closed_market_counterexample_pass_candidate():
    case = {
        "proposed_reject_reason": "pro-rata mulDiv is correct",
        "relied_upon_invariant": "sum of executed withdrawals <= batch.normalizedAmountPaid",
        "mechanism_class": "accounting",
        "counterexample_found": True,
        "counterexample_trace": "closed market: withdrawals execute before all requests batched; "
                                "scaledTotalAmount changes -> last user mulDiv share short -> under-withdraws",
    }
    r = A.evaluate(case)
    assert r.recommended_verdict == PASS_CANDIDATE
    assert r.counterexample


# ---- regression anchor 2: P95 M-05 grantRole inter-principal expiry bypass ----

def test_anchor_p95_m05_inter_principal_control_reopens():
    case = {
        "proposed_reject_reason": "trusted-provider only, not permissionless",
        "relied_upon_invariant": "only the original provider can lower a credential's expiry",
        "mechanism_class": "role",
        "inter_principal_trust_boundary": True,
        "ordering_cases_tested": ["same provider re-grants"],
        "counterexample_found": False,
    }
    assert A.evaluate(case).recommended_verdict == REOPEN


def test_anchor_p95_m05_provider_b_counterexample_pass_candidate():
    case = {
        "relied_upon_invariant": "only the original provider can lower a credential's expiry",
        "mechanism_class": "role", "inter_principal_trust_boundary": True,
        "counterexample_found": True,
        "counterexample_trace": "provider B calls grantRole with newExpiry < oldExpiry set by provider A",
    }
    assert A.evaluate(case).recommended_verdict == PASS_CANDIDATE


# ---- regression anchor 3: P85 updateTaxRate bounded eventual correction stays a REJECT ----

def test_anchor_p85_updatetaxrate_bounded_reject_confirmed():
    case = {
        "proposed_reject_reason": "lazy rate; eventual correction; bounded",
        "relied_upon_invariant": "tax accrues at the rate stored when a farm settles",
        "mechanism_class": "accounting",
        "ordering_cases_tested": ["update before settle", "update after settle", "two updates before one settle"],
        "boundary_cases_tested": ["rate=0", "rate=max"],
        "actor_interleavings_tested": ["admin updates between two users' settles"],
        "recovery_paths": ["self_correct"], "counterexample_found": False,
    }
    assert A.evaluate(case).recommended_verdict == REJECT_CONFIRMED


# ---- regression anchor 4: P81e H-01 fee-routing claimant-order dependence ----

def test_anchor_p81e_h01_claimant_order_pass_candidate():
    case = {
        "relied_upon_invariant": "each claimant receives only their own position's fees",
        "mechanism_class": "accounting", "counterexample_found": True,
        "counterexample_trace": "shared position: first claimant collect(max) siphons later claimants' fees",
    }
    assert A.evaluate(case).recommended_verdict == PASS_CANDIDATE


# ---- regression anchor 5: P87 M-18 forgeWithListed third-party race ----

def test_anchor_p87_m18_third_party_race_pass_candidate():
    case = {
        "relied_upon_invariant": "the lister's listed token is the one consumed by forgeWithListed",
        "mechanism_class": "state_order", "counterexample_found": True,
        "counterexample_trace": "third party relists the token between setup and the forge call",
    }
    assert A.evaluate(case).recommended_verdict == PASS_CANDIDATE


def test_anchor_p87_m18_untraced_reopens():
    case = {
        "relied_upon_invariant": "the lister's listed token is the one consumed by forgeWithListed",
        "mechanism_class": "state_order", "counterexample_found": False,
        "ordering_cases_tested": ["lister forges own token"],
    }
    assert A.evaluate(case).recommended_verdict == REOPEN


# ---- regression anchor 6: guarded onlyOwner control with no inter-principal boundary ----

def test_anchor_guarded_owner_control_reject_confirmed():
    case = {
        "relied_upon_invariant": "only the owner can call setConfig",
        "mechanism_class": "guarded_control", "inter_principal_trust_boundary": False,
        "counterexample_found": False,
    }
    assert A.evaluate(case).recommended_verdict == REJECT_CONFIRMED


# ---- supporting rules ----

def test_missing_invariant_reopens():
    assert A.evaluate({"mechanism_class": "accounting"}).recommended_verdict == REOPEN


def test_counterexample_without_trace_reopens():
    case = {"relied_upon_invariant": "inv", "mechanism_class": "accounting",
            "counterexample_found": True, "counterexample_trace": ""}
    assert A.evaluate(case).recommended_verdict == REOPEN


def test_unresolved_ordering_dependency_reopens():
    case = {"relied_upon_invariant": "inv", "mechanism_class": "accounting",
            "ordering_cases_tested": ["a", "b", "c"],
            "unresolved_ordering_dependency": "whether closeMarket can run mid-batch is unclear"}
    assert A.evaluate(case).recommended_verdict == REOPEN


def test_needs_execution_with_idea():
    case = {"relied_upon_invariant": "inv", "mechanism_class": "accounting",
            "ordering_cases_tested": ["a", "b", "c"], "needs_execution": True,
            "execution_test_idea": "Foundry: close market mid-batch, assert last user short"}
    assert A.evaluate(case).recommended_verdict == NEEDS_EXECUTION


def test_needs_execution_without_idea_reopens():
    case = {"relied_upon_invariant": "inv", "mechanism_class": "accounting",
            "ordering_cases_tested": ["a", "b", "c"], "needs_execution": True, "execution_test_idea": ""}
    assert A.evaluate(case).recommended_verdict == REOPEN


def test_other_class_not_force_reopened():
    case = {"relied_upon_invariant": "inv", "mechanism_class": "other", "counterexample_found": False}
    assert A.evaluate(case).recommended_verdict == REJECT_CONFIRMED


def test_orderings_count_sums_all_three_lists():
    case = {"relied_upon_invariant": "inv", "mechanism_class": "accounting",
            "ordering_cases_tested": ["a"], "boundary_cases_tested": ["b"],
            "actor_interleavings_tested": ["c"], "counterexample_found": False}
    r = A.evaluate(case)
    assert r.orderings_tested == 3
    assert r.recommended_verdict == REJECT_CONFIRMED


def test_two_orderings_accounting_reopens():
    case = {"relied_upon_invariant": "inv", "mechanism_class": "lifecycle",
            "ordering_cases_tested": ["a", "b"], "counterexample_found": False}
    assert A.evaluate(case).recommended_verdict == REOPEN


# ---- advisory / un-wired invariants ----

def test_result_emits_no_severity_field():
    case = {"relied_upon_invariant": "inv", "mechanism_class": "guarded_control"}
    assert "severity" not in A.evaluate(case)._asdict()


def test_flags_are_unwired():
    assert A.FLAGS["is_gate"] is False
    assert A.FLAGS["research_only"] is True
    assert A.FLAGS["routes_in_production"] is False
    assert A.FLAGS["routed_manifest_ids"] == []
