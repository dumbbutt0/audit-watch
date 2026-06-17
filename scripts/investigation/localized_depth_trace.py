#!/usr/bin/env python3
"""
localized_depth_trace.py — P92 ADVISORY depth-trace completeness check (RESEARCH-ONLY, UN-WIRED).

After the deep pass LOCALIZES a suspicious mechanism (see prompts/deep_pass_depth_trace_v3.md), this validates
that a CONCRETE execution trace was actually performed before any `NEEDS_CONTEXT` / harmless / Low conclusion is
honored. It repairs the recurring conversion-depth miss (P90-B's dominant `deep_pass` bucket; P91 M-02: the
calldata `endIndex - startIndex` off-by-one was localized but never traced to its concrete revert).

CORE EFFECT: make `NEEDS_CONTEXT` and generic "harmless" HARDER to emit. A bare `NEEDS_CONTEXT` (no named
missing dependency + next step) or a generic `REJECT` (no boundary-case trace) is downgraded to
`INSUFFICIENT_TRACE` — "trace the operation, or name the specific missing dependency." A TRACED bounded `REJECT`
(e.g. P85 updateTaxRate: eventual self-correction, no concrete consequence) IS still honored — reject-first is
preserved, not weakened.

It does NOT modify or call `severity_impact_gate` (frozen `193abf9f`), never sets severity, never converts a
REJECT into a finding, and never routes. It only checks trace COMPLETENESS and echoes the analyst's outcome when
the trace earns it. is_gate:false research_only:true review_only:true routes_in_production:false.
"""
from __future__ import annotations
import argparse
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional

ROOT = Path(__file__).resolve().parent.parent.parent
CFG = ROOT / "config" / "localized_depth_trace.json"
FLAGS = {"is_gate": False, "research_only": True, "review_only": True,
         "routes_in_production": False, "routed_manifest_ids": []}

INSUFFICIENT = "INSUFFICIENT_TRACE"


@lru_cache(maxsize=1)
def _cfg() -> dict:
    return json.loads(CFG.read_text())


class DepthTraceResult(NamedTuple):
    recommended_verdict: str   # PASS | REJECT | NEEDS_CONTEXT | INSUFFICIENT_TRACE  (advisory only)
    trace_complete: bool
    missing_fields: List[str]
    reasons: List[str]


def _nonempty(v: Any) -> bool:
    if v is None:
        return False
    if isinstance(v, str):
        return bool(v.strip())
    if isinstance(v, (list, tuple, dict)):
        return len(v) > 0
    return True


def evaluate(trace: Optional[Dict[str, Any]] = None) -> DepthTraceResult:
    """Validate a localized-mechanism depth trace and recommend a verdict.

    trace = {localized_mechanism, controlled_inputs, pre_state, operation_trace, boundary_cases, post_state,
             recovery_paths?, concrete_outcome, missing_evidence_if_any:{named_dependency,missing_value,next_step}}
    """
    cfg = _cfg()
    t = trace or {}
    reasons: List[str] = []

    # (0) completeness of the mandatory trace fields
    required = cfg["required_trace_fields"]
    missing = [f for f in required if not _nonempty(t.get(f))]
    complete = not missing
    if not complete:
        reasons.append(f"trace incomplete: missing/empty {missing} — complete the 5-step trace before concluding")
        return DepthTraceResult(INSUFFICIENT, False, missing, reasons)

    outcome = str(t.get("concrete_outcome", "") or "").upper()
    if outcome not in cfg["outcome_values"]:
        reasons.append(f"concrete_outcome must be one of {cfg['outcome_values']} (got {outcome or 'none'})")
        return DepthTraceResult(INSUFFICIENT, True, [], reasons)

    # (P94) completion gate: an IN-SCOPE next-step / in-scope callee must be RESOLVED before ANY conclusion.
    # This is a completion requirement, not an escalation rule — it never forces a positive verdict.
    in_scope_types = set(cfg.get("in_scope_next_step_types", []))
    oos_types = set(cfg.get("out_of_scope_next_step_types", []))
    nst = str(t.get("next_step_type", "") or "").upper()
    resolved = t.get("next_step_resolved") is True
    callee_in = t.get("callee_in_scope") is True
    if nst and nst not in in_scope_types and nst not in oos_types:
        reasons.append(f"next_step_type must be one of {sorted(in_scope_types | oos_types)} (got {nst})")
        return DepthTraceResult(INSUFFICIENT, True, [], reasons)
    in_scope_pending = (nst in in_scope_types) or callee_in
    if in_scope_pending and not resolved:
        what = "the in-scope callee at the staticcall/external boundary" if callee_in and nst not in in_scope_types \
            else f"the in-scope {nst.lower() or 'dependency'}"
        nxt = (t.get("missing_evidence_if_any") or {}).get("next_step") or t.get("next_step") or "read it / trace across the boundary"
        reasons.append(f"INSUFFICIENT: resolve {what} before concluding (next: {nxt}); an in-scope read/callee is resolvable from source — do not freeze on it")
        return DepthTraceResult(INSUFFICIENT, True, [], reasons)
    if in_scope_pending and resolved:
        if not _nonempty(t.get("resolved_evidence_ref")) or not _nonempty(t.get("final_trace_after_resolution")):
            reasons.append("INSUFFICIENT: next_step_resolved=true requires resolved_evidence_ref + final_trace_after_resolution (show the in-scope read/callee-trace result)")
            return DepthTraceResult(INSUFFICIENT, True, [], reasons)
    if outcome == "NEEDS_CONTEXT" and nst in in_scope_types:
        reasons.append("INSUFFICIENT: an in-scope dependency is resolvable from source — conclude PASS/REJECT after reading it; NEEDS_CONTEXT is only for out-of-scope / runtime / execution dependencies")
        return DepthTraceResult(INSUFFICIENT, True, [], reasons)

    op = _nonempty(t.get("operation_trace"))
    bc = _nonempty(t.get("boundary_cases"))
    ps = _nonempty(t.get("post_state"))

    # (1) PASS: must reach a concrete consequence through op + boundary + post_state
    if outcome == "PASS":
        if op and bc and ps:
            reasons.append("PASS honored: operation + boundary-case + post-state reach a concrete consequence")
            return DepthTraceResult("PASS", True, [], reasons)
        reasons.append("PASS not honored: a concrete bug path needs non-empty operation_trace + boundary_cases + post_state")
        return DepthTraceResult(INSUFFICIENT, True, [], reasons)

    # (2) REJECT: harmless/bounded/Low honored ONLY if boundary-case + post-state show source-backed
    #     self-correction / bounded-no-concrete (no generic 'looks fine'). A traced bounded REJECT IS allowed.
    if outcome == "REJECT":
        if bc and ps:
            reasons.append("REJECT honored: boundary-cases + post-state show a traced source-backed harmless/bounded outcome (reject-first preserved)")
            return DepthTraceResult("REJECT", True, [], reasons)
        reasons.append("REJECT not honored: a harmless/bounded conclusion needs a boundary-case + post-state trace, not a generic 'looks fine'")
        return DepthTraceResult(INSUFFICIENT, True, [], reasons)

    # (3) NEEDS_CONTEXT: harder to emit — requires a named missing dependency + next step AND a real trace attempt
    if outcome == "NEEDS_CONTEXT":
        me = t.get("missing_evidence_if_any") or {}
        need = cfg["needs_context_required_evidence"]
        missing_ev = [k for k in need if not _nonempty(me.get(k))]
        if missing_ev:
            reasons.append(f"NEEDS_CONTEXT not honored: missing {missing_ev} — name the specific dependency, the missing value, and the next step (do not abstain in place of tracing)")
            return DepthTraceResult(INSUFFICIENT, True, [], reasons)
        if not (op and bc):
            reasons.append("NEEDS_CONTEXT not honored: trace the operation/boundary first; abstain only AFTER the trace reaches a specific unknown dependency")
            return DepthTraceResult(INSUFFICIENT, True, [], reasons)
        reasons.append("NEEDS_CONTEXT honored: trace performed and a specific missing dependency + next step are named")
        return DepthTraceResult("NEEDS_CONTEXT", True, [], reasons)

    return DepthTraceResult(INSUFFICIENT, True, [], ["unreachable"])


def _self_test() -> int:
    ok = True
    def chk(c, m):
        nonlocal ok; ok &= bool(c); print(f"  [{'PASS' if c else 'FAIL'}] {m}")

    base = {
        "localized_mechanism": "Timelock.checkCalldata length math",
        "controlled_inputs": "hot signer payload bytes",
        "pre_state": "calldataCheck.startIndex/endIndex set by governance",
        "post_state": "whitelisted call reverts",
    }
    # P91 M-02: full trace + concrete revert -> PASS honored
    m02 = dict(base, operation_trace="length = endIndex - startIndex (missing +1) -> getSlicedBytesHash short by 1 byte",
               boundary_cases="param fills all 32 bytes -> slice is 31 bytes -> hash mismatch -> require revert",
               concrete_outcome="PASS")
    chk(evaluate(m02).recommended_verdict == "PASS", "P91 M-02 traced -> PASS honored")
    # same mechanism, bare NEEDS_CONTEXT (no named dep) -> INSUFFICIENT_TRACE (the core fix)
    bare = dict(base, operation_trace="length = endIndex - startIndex", boundary_cases="",
                concrete_outcome="NEEDS_CONTEXT", missing_evidence_if_any={})
    chk(evaluate(bare).recommended_verdict == INSUFFICIENT, "bare NEEDS_CONTEXT (no named dep) -> INSUFFICIENT_TRACE")
    # well-formed NEEDS_CONTEXT (named dep + next step + trace attempted) -> honored
    nc = dict(base, operation_trace="reads getSlicedBytesHash from BytesHelper",
              boundary_cases="depends on the runtime value returned by an out-of-scope BytesHelper build",
              concrete_outcome="NEEDS_CONTEXT",
              missing_evidence_if_any={"named_dependency": "BytesHelper.getSlicedBytesHash impl",
                                       "missing_value": "actual sliced length for a 32-byte param",
                                       "next_step": "read src/BytesHelper.sol:getSlicedBytesHash"})
    chk(evaluate(nc).recommended_verdict == "NEEDS_CONTEXT", "well-formed NEEDS_CONTEXT honored")
    # P85 updateTaxRate: traced bounded REJECT -> honored (reject-first intact, depth doesn't force PASS)
    utr = dict(base, localized_mechanism="updateTaxRate settlement", operation_trace="rate applied lazily next settle",
               boundary_cases="next farm settles at correct rate; difference is bounded and self-corrects",
               post_state="no permanent loss; eventual correction", concrete_outcome="REJECT")
    chk(evaluate(utr).recommended_verdict == "REJECT", "P85 updateTaxRate traced bounded -> REJECT honored")
    # generic harmless REJECT (no boundary trace) -> INSUFFICIENT_TRACE
    gen = dict(base, operation_trace="looks standard", boundary_cases="", post_state="", concrete_outcome="REJECT")
    chk(evaluate(gen).recommended_verdict == INSUFFICIENT, "generic harmless REJECT (no boundary trace) -> INSUFFICIENT_TRACE")
    # incomplete trace (missing a required field) -> INSUFFICIENT_TRACE
    inc = {"localized_mechanism": "x", "concrete_outcome": "PASS"}
    r = evaluate(inc); chk(r.recommended_verdict == INSUFFICIENT and not r.trace_complete, "incomplete trace -> INSUFFICIENT_TRACE")
    # other PASS anchors (full traces) honored
    for name, mech in [("P89 H-05", "public _add/_removeCredIdPerAddress index"),
                       ("P89 M-07", "buyShareCredFor lastTradeTimestamp reset"),
                       ("P87 H-01", "global _tokenIds vs per-gen maxTokensPerGen"),
                       ("P85 H-05", "dirty flag never reset"),
                       ("P81e H-01", "shared position collect(max) routes fees to feeTaker")]:
        tr = dict(base, localized_mechanism=mech, operation_trace="traced", boundary_cases="edge case traced",
                  post_state="concrete consequence", concrete_outcome="PASS")
        chk(evaluate(tr).recommended_verdict == "PASS", f"{name} full trace -> PASS honored")

    # ---- P94 completion gate ----
    # P93 M-02: next_step="read flash body" IN_SCOPE_READ unresolved -> INSUFFICIENT (cannot freeze)
    flash_unres = dict(base, localized_mechanism="RamsesV3Pool.flash protocol fee",
                       operation_trace="pFees0 = paid0 / feeProtocol (need to read the flash body to confirm)",
                       boundary_cases="pending read", post_state="pending", concrete_outcome="NEEDS_CONTEXT",
                       next_step_type="IN_SCOPE_READ", next_step_resolved=False,
                       missing_evidence_if_any={"named_dependency": "RamsesV3Pool.flash body", "missing_value": "exact pFees expr", "next_step": "read RamsesV3Pool.flash"})
    chk(evaluate(flash_unres).recommended_verdict == INSUFFICIENT, "P93 M-02 unresolved IN_SCOPE_READ -> INSUFFICIENT_TRACE")
    # P93 M-02 completed: read flash, found paid0/feeProtocol -> PASS honored
    flash_done = dict(base, localized_mechanism="RamsesV3Pool.flash protocol fee",
                      operation_trace="pFees0 = paid0 / feeProtocol",
                      boundary_cases="feeProtocol=80 -> protocol gets paid0/80 = 1/80 instead of 80%",
                      post_state="protocol receives ~1/80 of intended fees", concrete_outcome="PASS",
                      next_step_type="IN_SCOPE_READ", next_step_resolved=True,
                      resolved_evidence_ref="RamsesV3Pool.sol flash() pFees0 line",
                      final_trace_after_resolution="confirmed divide-not-multiply; protocol underpaid")
    chk(evaluate(flash_done).recommended_verdict == "PASS", "P93 M-02 resolved IN_SCOPE_READ -> PASS honored")
    # P93 M-01: callee_in_scope staticcall boundary, unresolved -> INSUFFICIENT
    m01_boundary = dict(base, localized_mechanism="GaugeV3.cachePeriodEarned -> pool.positionPeriodSecondsInRange",
                        operation_trace="staticcall positionPeriodSecondsInRange", boundary_cases="stopped at boundary",
                        post_state="unknown", concrete_outcome="REJECT",
                        next_step_type="IN_SCOPE_CALL_TRACE", next_step_resolved=False, callee_in_scope=True)
    chk(evaluate(m01_boundary).recommended_verdict == INSUFFICIENT, "P93 M-01 in-scope callee boundary unresolved -> INSUFFICIENT_TRACE")
    # P93 M-01 completed: traced into pool periodCumulativesInside skipped-period case -> PASS
    m01_done = dict(base, localized_mechanism="pool.periodCumulativesInside skipped-period",
                    operation_trace="endSecondsPerLiquidityPeriodX128 used when currentPeriod>period",
                    boundary_cases="skipped period inflates secondsInside -> reward over-credit",
                    post_state="inflated GaugeV3 rewards", concrete_outcome="PASS",
                    next_step_type="IN_SCOPE_CALL_TRACE", next_step_resolved=True, callee_in_scope=True,
                    resolved_evidence_ref="RamsesV3Pool periodCumulativesInside else-branch",
                    final_trace_after_resolution="skipped-period branch over-counts seconds")
    chk(evaluate(m01_done).recommended_verdict == "PASS", "P93 M-01 resolved cross-contract trace -> PASS honored")
    # in-scope dependency resolvable -> NEEDS_CONTEXT not allowed (must conclude)
    isc_nc = dict(flash_unres, concrete_outcome="NEEDS_CONTEXT", next_step_resolved=True,
                  resolved_evidence_ref="ref", final_trace_after_resolution="trace")
    chk(evaluate(isc_nc).recommended_verdict == INSUFFICIENT, "resolved IN_SCOPE + NEEDS_CONTEXT -> INSUFFICIENT (must conclude PASS/REJECT)")
    # genuine OUT_OF_SCOPE dependency -> NEEDS_CONTEXT still allowed
    oos = dict(base, localized_mechanism="FeeCollector.collectProtocolFees -> FeeDistributor.notifyRewardAmount",
               operation_trace="approve then external notifyRewardAmount", boundary_cases="depends on out-of-scope FeeDistributor allowance consumption",
               post_state="depends on external", concrete_outcome="NEEDS_CONTEXT",
               next_step_type="OUT_OF_SCOPE_DEPENDENCY", next_step_resolved=False,
               unresolved_reason="FeeDistributor is out of scope / not vendored",
               missing_evidence_if_any={"named_dependency": "IFeeDistributor.notifyRewardAmount", "missing_value": "full-allowance consumption", "next_step": "obtain out-of-scope FeeDistributor"})
    chk(evaluate(oos).recommended_verdict == "NEEDS_CONTEXT", "genuine OUT_OF_SCOPE dependency -> NEEDS_CONTEXT allowed")
    # resolved in-scope claimed but no evidence -> INSUFFICIENT
    noev = dict(flash_done, resolved_evidence_ref="", final_trace_after_resolution="")
    chk(evaluate(noev).recommended_verdict == INSUFFICIENT, "resolved=true without evidence/final_trace -> INSUFFICIENT")

    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--json", help="trace JSON")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    t = json.loads(args.json) if args.json else {}
    print(json.dumps(evaluate(t)._asdict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
