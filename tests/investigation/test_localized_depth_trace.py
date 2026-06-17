"""P92 tests for the advisory localized depth-trace completeness check (RESEARCH-ONLY, un-wired).

Regression anchors (frozen misses): P91 M-02, P89 H-05, P89 M-07, P87 H-01, P85 H-05, P85 updateTaxRate (REJECT
still honored), P81e H-01 — plus the NEEDS_CONTEXT / harmless gating that makes a bare abstain INSUFFICIENT.
The check is advisory: it validates trace COMPLETENESS and echoes the analyst's outcome when earned; it never
sets severity, never routes, never converts a REJECT into a finding.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "investigation"))
from investigation import localized_depth_trace as D  # noqa: E402

INSUFFICIENT = D.INSUFFICIENT


def _base(**over):
    t = {
        "localized_mechanism": "Contract.fn expr",
        "controlled_inputs": "attacker input + bounds + entrypoint",
        "pre_state": "named storage before",
        "operation_trace": "traced expression",
        "boundary_cases": "edge case + hand result",
        "post_state": "what changed / recoverability",
    }
    t.update(over)
    return t


def test_self_test_passes():
    assert D._self_test() == 0


# ---- regression anchors ----

def test_anchor_p91_m02_traced_pass_honored():
    t = _base(localized_mechanism="checkCalldata length = endIndex-startIndex",
              operation_trace="length = endIndex - startIndex (missing +1)",
              boundary_cases="param fills all 32 bytes -> slice 31 bytes -> hash mismatch -> revert",
              post_state="whitelisted call reverts", concrete_outcome="PASS")
    assert D.evaluate(t).recommended_verdict == "PASS"


def test_anchor_p91_m02_bare_needs_context_is_insufficient():
    t = _base(operation_trace="length = endIndex - startIndex", boundary_cases="",
              concrete_outcome="NEEDS_CONTEXT", missing_evidence_if_any={})
    r = D.evaluate(t)
    assert r.recommended_verdict == INSUFFICIENT


def test_anchor_p89_h05_pass():
    t = _base(localized_mechanism="public _add/_removeCredIdPerAddress index",
              operation_trace="public mutator writes _credIdsPerAddressCredIdIndex for arbitrary address",
              boundary_cases="attacker overwrites index -> later removeCredId reverts IndexOutofBounds",
              post_state="victim sell reverts", concrete_outcome="PASS")
    assert D.evaluate(t).recommended_verdict == "PASS"


def test_anchor_p89_m07_involuntary_pass():
    t = _base(localized_mechanism="buyShareCredFor resets lastTradeTimestamp[curator]",
              operation_trace="third party calls buyShareCredFor(curator=victim) -> lastTradeTimestamp=now",
              boundary_cases="involuntary: harmed party (victim) != actor; victim's sell-lock never elapses",
              post_state="victim cannot sell", concrete_outcome="PASS")
    assert D.evaluate(t).recommended_verdict == "PASS"


def test_anchor_p87_h01_counter_scope_pass():
    t = _base(localized_mechanism="mintWithBudget loop guard _tokenIds < maxTokensPerGen",
              operation_trace="global _tokenIds vs per-generation cap",
              boundary_cases="global supply hits 10000 -> loop never runs from gen2 on",
              post_state="budget-mint path permanently bricked", concrete_outcome="PASS")
    assert D.evaluate(t).recommended_verdict == "PASS"


def test_anchor_p85_h05_dirty_flag_pass():
    t = _base(localized_mechanism="dirty flag set, never reset",
              operation_trace="dirty=true in _farmPlots; cleared only on stake/unstake",
              boundary_cases="token returns to valid plot via transferToUnoccupiedPlot -> dirty stays true",
              post_state="permanent reward-accrual loss", concrete_outcome="PASS")
    assert D.evaluate(t).recommended_verdict == "PASS"


def test_anchor_p85_updatetaxrate_traced_reject_honored():
    # reject-first preserved: a TRACED bounded/self-correcting outcome is still a valid REJECT (not forced to PASS)
    t = _base(localized_mechanism="updateTaxRate lazy settlement",
              operation_trace="rate applied at next settle; no settlement at change time",
              boundary_cases="interval re-priced at the next farm; difference bounded; eventual self-correction",
              post_state="no permanent loss; no concrete material consequence", concrete_outcome="REJECT")
    assert D.evaluate(t).recommended_verdict == "REJECT"


def test_anchor_p81e_h01_fee_routing_pass():
    t = _base(localized_mechanism="ILOPool.claim collect(max,max) on shared position",
              operation_trace="burn credits all LP fees; collect(max) pulls whole position; residual -> feeTaker",
              boundary_cases="second claimant after first: owed fees already swept -> claim reverts",
              post_state="non-first claimant loses fees / cannot claim", concrete_outcome="PASS")
    assert D.evaluate(t).recommended_verdict == "PASS"


# ---- gating: NEEDS_CONTEXT / harmless harder to emit ----

def test_well_formed_needs_context_honored():
    t = _base(operation_trace="reads getSlicedBytesHash",
              boundary_cases="depends on runtime value from out-of-scope BytesHelper build",
              concrete_outcome="NEEDS_CONTEXT",
              missing_evidence_if_any={"named_dependency": "BytesHelper.getSlicedBytesHash",
                                       "missing_value": "sliced length for 32-byte param",
                                       "next_step": "read src/BytesHelper.sol"})
    assert D.evaluate(t).recommended_verdict == "NEEDS_CONTEXT"


def test_needs_context_missing_next_step_insufficient():
    t = _base(operation_trace="x", boundary_cases="y", concrete_outcome="NEEDS_CONTEXT",
              missing_evidence_if_any={"named_dependency": "Foo.bar", "missing_value": "v"})  # no next_step
    assert D.evaluate(t).recommended_verdict == INSUFFICIENT


def test_generic_harmless_reject_without_boundary_is_insufficient():
    t = _base(operation_trace="looks standard", boundary_cases="", post_state="", concrete_outcome="REJECT")
    assert D.evaluate(t).recommended_verdict == INSUFFICIENT


def test_incomplete_trace_is_insufficient():
    r = D.evaluate({"localized_mechanism": "x", "concrete_outcome": "PASS"})
    assert r.recommended_verdict == INSUFFICIENT and r.trace_complete is False and r.missing_fields


def test_pass_without_concrete_boundary_is_insufficient():
    t = _base(boundary_cases="", post_state="", concrete_outcome="PASS")
    assert D.evaluate(t).recommended_verdict == INSUFFICIENT


# ---- P94 completion-gate regression anchors ----

def test_p94_anchor1_m02_unresolved_in_scope_read_insufficient():
    # next_step "read flash body" is IN_SCOPE_READ, not resolved -> cannot freeze (even as NEEDS_CONTEXT)
    t = _base(localized_mechanism="RamsesV3Pool.flash protocol fee",
              operation_trace="pFees0 = paid0 / feeProtocol (need to read flash body)",
              boundary_cases="pending", post_state="pending", concrete_outcome="NEEDS_CONTEXT",
              next_step_type="IN_SCOPE_READ", next_step_resolved=False,
              missing_evidence_if_any={"named_dependency": "flash body", "missing_value": "pFees expr", "next_step": "read RamsesV3Pool.flash"})
    assert D.evaluate(t).recommended_verdict == INSUFFICIENT


def test_p94_anchor1_m02_resolved_read_reaches_pass():
    t = _base(localized_mechanism="RamsesV3Pool.flash protocol fee",
              operation_trace="pFees0 = paid0 / feeProtocol",
              boundary_cases="feeProtocol=80 -> protocol gets paid0/80 = 1/80 not 80%",
              post_state="protocol underpaid ~80x", concrete_outcome="PASS",
              next_step_type="IN_SCOPE_READ", next_step_resolved=True,
              resolved_evidence_ref="RamsesV3Pool.flash pFees0 line",
              final_trace_after_resolution="divide instead of multiply confirmed")
    assert D.evaluate(t).recommended_verdict == "PASS"


def test_p94_anchor2_m01_in_scope_callee_boundary_insufficient():
    # trace stops at an in-scope staticcall boundary (callee_in_scope) -> must trace across
    t = _base(localized_mechanism="GaugeV3.cachePeriodEarned -> pool.positionPeriodSecondsInRange",
              operation_trace="staticcall positionPeriodSecondsInRange", boundary_cases="stopped at boundary",
              post_state="unknown", concrete_outcome="REJECT",
              next_step_type="IN_SCOPE_CALL_TRACE", next_step_resolved=False, callee_in_scope=True)
    assert D.evaluate(t).recommended_verdict == INSUFFICIENT


def test_p94_anchor2_m01_cross_contract_trace_reaches_pass():
    t = _base(localized_mechanism="pool.periodCumulativesInside skipped-period",
              operation_trace="endSecondsPerLiquidityPeriodX128 used when currentPeriod>period",
              boundary_cases="skipped period over-counts secondsInside -> reward inflation",
              post_state="inflated GaugeV3 rewards", concrete_outcome="PASS",
              next_step_type="IN_SCOPE_CALL_TRACE", next_step_resolved=True, callee_in_scope=True,
              resolved_evidence_ref="pool periodCumulativesInside else-branch",
              final_trace_after_resolution="over-count confirmed")
    assert D.evaluate(t).recommended_verdict == "PASS"


def test_p94_anchor3_p91_m02_calldata_still_concrete():
    # P91 M-02 calldata arithmetic still needs concrete trace (no new field needed) -> PASS
    t = _base(operation_trace="length = endIndex - startIndex (no +1)",
              boundary_cases="param fills all 32 bytes -> slice short -> revert", concrete_outcome="PASS")
    assert D.evaluate(t).recommended_verdict == "PASS"


def test_p94_anchor4_updatetaxrate_completed_bounded_reject():
    # completed bounded/lazy trace with no concrete consequence remains REJECT (no forced positive verdict)
    t = _base(localized_mechanism="updateTaxRate", operation_trace="rate applied lazily next settle",
              boundary_cases="next farm settles correctly; bounded; self-corrects",
              post_state="no permanent loss", concrete_outcome="REJECT",
              next_step_type="IN_SCOPE_READ", next_step_resolved=True,
              resolved_evidence_ref="updateTaxRate body", final_trace_after_resolution="no settlement-at-change; lazy but bounded")
    assert D.evaluate(t).recommended_verdict == "REJECT"


def test_p94_anchor5_p81e_fee_routing_cross_function_pass():
    t = _base(localized_mechanism="ILOPool.claim collect(max) shared position",
              operation_trace="burn credits all LP fees; collect(max) pulls whole position; residual->feeTaker",
              boundary_cases="second claimant: fees already swept -> claim reverts",
              post_state="non-first claimant loses/cannot claim", concrete_outcome="PASS",
              next_step_type="IN_SCOPE_CALL_TRACE", next_step_resolved=True, callee_in_scope=True,
              resolved_evidence_ref="ILOPool.claim collect+feeTaker lines", final_trace_after_resolution="order-dependent loss confirmed")
    assert D.evaluate(t).recommended_verdict == "PASS"


def test_p94_anchor6_out_of_scope_dependency_allows_needs_context():
    t = _base(localized_mechanism="FeeCollector -> external FeeDistributor",
              operation_trace="approve + external notifyRewardAmount", boundary_cases="depends on out-of-scope FeeDistributor",
              post_state="depends on external", concrete_outcome="NEEDS_CONTEXT",
              next_step_type="OUT_OF_SCOPE_DEPENDENCY", next_step_resolved=False,
              unresolved_reason="FeeDistributor out of scope / not vendored",
              missing_evidence_if_any={"named_dependency": "IFeeDistributor.notifyRewardAmount", "missing_value": "allowance consumption", "next_step": "obtain out-of-scope contract"})
    assert D.evaluate(t).recommended_verdict == "NEEDS_CONTEXT"


def test_p94_resolved_without_evidence_insufficient():
    t = _base(operation_trace="x", boundary_cases="y", post_state="z", concrete_outcome="PASS",
              next_step_type="IN_SCOPE_READ", next_step_resolved=True)  # no evidence/final_trace
    assert D.evaluate(t).recommended_verdict == INSUFFICIENT


def test_p94_invalid_next_step_type_insufficient():
    t = _base(operation_trace="x", boundary_cases="y", post_state="z", concrete_outcome="PASS",
              next_step_type="BOGUS")
    assert D.evaluate(t).recommended_verdict == INSUFFICIENT


def test_p94_legacy_p92_trace_unaffected():
    # a P92-style trace with NO completion fields behaves exactly as before
    t = _base(operation_trace="traced", boundary_cases="edge", post_state="consequence", concrete_outcome="PASS")
    assert D.evaluate(t).recommended_verdict == "PASS"


def test_self_test_passes_incl_p94():
    assert D._self_test() == 0


def test_advisory_flags_and_no_severity_field():
    assert D.FLAGS["is_gate"] is False and D.FLAGS["routes_in_production"] is False
    r = D.evaluate(_base(concrete_outcome="PASS"))
    assert set(r._fields) == {"recommended_verdict", "trace_complete", "missing_fields", "reasons"}
    # no severity/routing concepts emitted
    assert "severity" not in r._fields and "route" not in r._fields
