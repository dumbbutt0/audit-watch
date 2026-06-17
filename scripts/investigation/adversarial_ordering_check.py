#!/usr/bin/env python3
"""
adversarial_ordering_check.py — P96 ADVISORY adversarial state-ordering & boundary-enumeration check
(RESEARCH-ONLY, UN-WIRED).

After the deep pass localizes a mechanism AND the depth-trace COMPLETES (localized_depth_trace.py P92/P94),
this is a SECOND gate before a REJECT/harmless/Low may be FINALIZED. It forces the analyst to (a) state the
invariant the REJECT relies on, then (b) actively try to BREAK it with concrete adversarial state orderings,
boundary cases and actor interleavings before the REJECT is honored.

WHY: P95 (wildcat) produced two completed-but-WRONG REJECTs that P92/P94 could not catch because the trace was
*done*, not adversarially complete:
  - H-01 executeWithdrawal: pro-rata `mulDiv(batch.normalizedAmountPaid, status.scaledAmount,
    batch.scaledTotalAmount)` read as locally correct, but the CLOSED-MARKET early-execution ordering breaks the
    `sum <= batch.normalizedAmountPaid` invariant -> last user under-withdraws. The trace never enumerated that
    ordering.
  - M-05 grantRole: the provider-vs-provider expiry-replacement rule was dismissed as a "trusted control"
    without enumerating the inter-principal (provider A vs provider B) ordering that bypasses it.

CORE EFFECT: a localized, completed REJECT on an accounting / lifecycle / role / state-order mechanism may only
be FINALIZED (REJECT_CONFIRMED) after >=3 concrete orderings have been tried with no counterexample; an
inter-principal trust boundary may not be dismissed as a trusted control without that same enumeration; a found
counterexample makes the mechanism a PASS_CANDIDATE (not a REJECT); a trace that only lacks execution becomes
NEEDS_EXECUTION with a test idea. Guarded single-principal controls with no inter-principal boundary still
REJECT_CONFIRMED — reject-first is preserved, not weakened.

It does NOT modify or call `severity_impact_gate` (frozen `193abf9f`), never sets severity, never converts a
REJECT into a finding, and never routes. It only decides whether a REJECT may be FINALIZED vs must reopen the
depth trace. is_gate:false research_only:true review_only:true routes_in_production:false.
"""
from __future__ import annotations
import argparse
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional

ROOT = Path(__file__).resolve().parent.parent.parent
CFG = ROOT / "config" / "adversarial_ordering_check.json"
FLAGS = {"is_gate": False, "research_only": True, "review_only": True,
         "routes_in_production": False, "routed_manifest_ids": []}

REJECT_CONFIRMED = "REJECT_CONFIRMED"
REOPEN = "REOPEN_DEPTH_TRACE"
NEEDS_EXECUTION = "NEEDS_EXECUTION"
PASS_CANDIDATE = "PASS_CANDIDATE"


@lru_cache(maxsize=1)
def _cfg() -> dict:
    return json.loads(CFG.read_text())


class AdversarialOrderingResult(NamedTuple):
    recommended_verdict: str   # REJECT_CONFIRMED | REOPEN_DEPTH_TRACE | NEEDS_EXECUTION | PASS_CANDIDATE
    orderings_tested: int
    counterexample: Optional[str]
    reasons: List[str]


def _nonempty(v: Any) -> bool:
    if v is None:
        return False
    if isinstance(v, str):
        return bool(v.strip())
    if isinstance(v, (list, tuple, dict)):
        return len(v) > 0
    return True


def _as_list(v: Any) -> list:
    if v is None:
        return []
    if isinstance(v, (list, tuple)):
        return [x for x in v if _nonempty(x)]
    if _nonempty(v):
        return [v]
    return []


def evaluate(case: Optional[Dict[str, Any]] = None) -> AdversarialOrderingResult:
    """Decide whether a localized, completed REJECT may be FINALIZED or must reopen the depth trace.

    case = {proposed_reject_reason, relied_upon_invariant, mechanism_class,
            ordering_cases_tested[], boundary_cases_tested[], actor_interleavings_tested[], recovery_paths[],
            counterexample_found:bool, counterexample_trace, unresolved_ordering_dependency,
            inter_principal_trust_boundary:bool, needs_execution:bool, execution_test_idea}
    """
    cfg = _cfg()
    c = case or {}
    reasons: List[str] = []

    orderings = (_as_list(c.get("ordering_cases_tested"))
                 + _as_list(c.get("boundary_cases_tested"))
                 + _as_list(c.get("actor_interleavings_tested")))
    n = len(orderings)
    min_n = int(cfg.get("min_orderings", 3))
    mclass = str(c.get("mechanism_class", "") or "").strip().lower()
    requires_3 = set(cfg.get("mechanism_classes_requiring_3", []))
    counterexample_trace = c.get("counterexample_trace")

    # (1) must state the invariant the REJECT relies on
    if not _nonempty(c.get("relied_upon_invariant")):
        reasons.append("REOPEN: state the relied_upon_invariant the REJECT depends on, then try to break it")
        return AdversarialOrderingResult(REOPEN, n, None, reasons)

    # (2) a found counterexample is NOT a REJECT — it is a PASS_CANDIDATE (needs a concrete trace)
    if c.get("counterexample_found") is True:
        if _nonempty(counterexample_trace):
            reasons.append("PASS_CANDIDATE: a concrete ordering breaks the relied-upon invariant — not a REJECT")
            return AdversarialOrderingResult(PASS_CANDIDATE, n, str(counterexample_trace), reasons)
        reasons.append("REOPEN: counterexample claimed but counterexample_trace is empty — trace the breaking ordering concretely")
        return AdversarialOrderingResult(REOPEN, n, None, reasons)

    # (3) an unresolved ordering dependency means the enumeration is not finished
    if _nonempty(c.get("unresolved_ordering_dependency")):
        reasons.append(f"REOPEN: unresolved ordering dependency — {c.get('unresolved_ordering_dependency')}")
        return AdversarialOrderingResult(REOPEN, n, None, reasons)

    # (4) an inter-principal trust boundary may NOT be dismissed as a trusted control without enumeration (M-05)
    if c.get("inter_principal_trust_boundary") is True and n < min_n:
        reasons.append(f"REOPEN: inter-principal trust boundary (e.g. provider-vs-provider) needs >={min_n} concrete orderings "
                       f"before it may be dismissed as a trusted control (tested {n})")
        return AdversarialOrderingResult(REOPEN, n, None, reasons)

    # (5) accounting/lifecycle/role/state-order REJECT needs >=3 concrete orderings tried (H-01)
    if mclass in requires_3 and n < min_n:
        reasons.append(f"REOPEN: a '{mclass}' REJECT needs >={min_n} concrete adversarial orderings tried "
                       f"(lifecycle + actor + accounting-boundary) before finalizing; only {n} tested")
        return AdversarialOrderingResult(REOPEN, n, None, reasons)

    # (6) only-missing-execution -> NEEDS_EXECUTION with a concrete test idea
    if c.get("needs_execution") is True:
        if _nonempty(c.get("execution_test_idea")):
            reasons.append("NEEDS_EXECUTION: orderings enumerated; the remaining unknown is runtime/execution — propose the test")
            return AdversarialOrderingResult(NEEDS_EXECUTION, n, None, reasons)
        reasons.append("REOPEN: needs_execution claimed without an execution_test_idea — name the concrete test to run")
        return AdversarialOrderingResult(REOPEN, n, None, reasons)

    # (7) guarded single-principal control (no inter-principal boundary), or a fully-enumerated >=3-ordering
    #     trace with no counterexample -> REJECT may be finalized (reject-first preserved)
    if mclass == "guarded_control":
        reasons.append("REJECT_CONFIRMED: guarded single-principal control with no inter-principal boundary and no counterexample")
        return AdversarialOrderingResult(REJECT_CONFIRMED, n, None, reasons)
    reasons.append(f"REJECT_CONFIRMED: {n} adversarial orderings tried, none breaks the relied-upon invariant")
    return AdversarialOrderingResult(REJECT_CONFIRMED, n, None, reasons)


def _self_test() -> int:
    ok = True
    def chk(cond, m):
        nonlocal ok; ok &= bool(cond); print(f"  [{'PASS' if cond else 'FAIL'}] {m}")

    inv = "sum of executed withdrawals <= batch.normalizedAmountPaid"

    # (1) P95 H-01 executeWithdrawal: accounting, pro-rata read locally correct, NO closed-market ordering -> REOPEN
    h01_local = {
        "proposed_reject_reason": "pro-rata mulDiv is correct; accounting consistent",
        "relied_upon_invariant": inv, "mechanism_class": "accounting",
        "ordering_cases_tested": ["open market, single withdrawal"],
        "counterexample_found": False,
    }
    chk(evaluate(h01_local).recommended_verdict == REOPEN, "P95 H-01 local pro-rata REJECT (no closed-market ordering) -> REOPEN")
    # H-01 with the closed-market early-execution counterexample found -> PASS_CANDIDATE
    h01_cex = dict(h01_local, counterexample_found=True,
                   counterexample_trace="closed market: withdrawals execute before all requests batched; "
                                        "scaledTotalAmount grows after early exec -> last user mulDiv share short -> under-withdraws")
    chk(evaluate(h01_cex).recommended_verdict == PASS_CANDIDATE, "P95 H-01 closed-market counterexample -> PASS_CANDIDATE")

    # (2) P95 M-05 grantRole: inter-principal boundary dismissed as trusted control (<3 orderings) -> REOPEN
    m05_control = {
        "proposed_reject_reason": "trusted-provider only, not permissionless",
        "relied_upon_invariant": "only the original provider can lower a credential's expiry",
        "mechanism_class": "role", "inter_principal_trust_boundary": True,
        "ordering_cases_tested": ["same provider re-grants"],
        "counterexample_found": False,
    }
    chk(evaluate(m05_control).recommended_verdict == REOPEN, "P95 M-05 inter-principal boundary as trusted control (<3) -> REOPEN")
    # M-05 with provider-B-lowers-expiry counterexample -> PASS_CANDIDATE
    m05_cex = dict(m05_control, counterexample_found=True,
                   counterexample_trace="provider B (also a role provider) calls grantRole with newExpiry < oldExpiry "
                                        "set by provider A -> A's credential window shortened by a different principal")
    chk(evaluate(m05_cex).recommended_verdict == PASS_CANDIDATE, "P95 M-05 provider-B counterexample -> PASS_CANDIDATE")

    # (3) P85 updateTaxRate: accounting, >=3 orderings tried, bounded eventual correction, no counterexample -> REJECT_CONFIRMED
    utr = {
        "proposed_reject_reason": "lazy rate; eventual correction; bounded",
        "relied_upon_invariant": "tax accrues at the rate stored when a farm settles",
        "mechanism_class": "accounting",
        "ordering_cases_tested": ["update before settle", "update after settle", "two updates before one settle"],
        "boundary_cases_tested": ["rate set to 0", "rate set to max"],
        "actor_interleavings_tested": ["admin updates between two users' settles"],
        "recovery_paths": ["self_correct"], "counterexample_found": False,
    }
    chk(evaluate(utr).recommended_verdict == REJECT_CONFIRMED, "P85 updateTaxRate >=3 orderings, bounded -> REJECT_CONFIRMED")

    # (4) P81e H-01 fee-routing: claimant-order dependence counterexample -> PASS_CANDIDATE
    fee = {
        "proposed_reject_reason": "fees route to feeTaker as designed",
        "relied_upon_invariant": "each claimant receives only their own position's fees",
        "mechanism_class": "accounting", "counterexample_found": True,
        "counterexample_trace": "shared position: first claimant calls collect(max) and siphons later claimants' "
                                "accrued fees -> outcome depends on claimant ordering",
    }
    chk(evaluate(fee).recommended_verdict == PASS_CANDIDATE, "P81e H-01 claimant-order fee-routing counterexample -> PASS_CANDIDATE")

    # (5) P87 M-18 forgeWithListed: third-party race interleaving counterexample -> PASS_CANDIDATE
    forge = {
        "proposed_reject_reason": "forge consumes the listed token as expected",
        "relied_upon_invariant": "the lister's listed token is the one consumed by forgeWithListed",
        "mechanism_class": "state_order", "counterexample_found": True,
        "counterexample_trace": "third party buys/relists the listed token between the lister's setup and the "
                                "forge call -> forge consumes a swapped token / wrong owner",
    }
    chk(evaluate(forge).recommended_verdict == PASS_CANDIDATE, "P87 M-18 third-party race counterexample -> PASS_CANDIDATE")
    # P87 M-18 not yet traced (state_order, <3 orderings, no counterexample) -> REOPEN
    forge_untraced = {
        "proposed_reject_reason": "forge looks fine",
        "relied_upon_invariant": "the lister's listed token is the one consumed by forgeWithListed",
        "mechanism_class": "state_order", "counterexample_found": False,
        "ordering_cases_tested": ["lister forges own token"],
    }
    chk(evaluate(forge_untraced).recommended_verdict == REOPEN, "P87 M-18 untraced state_order (<3) -> REOPEN")

    # (6) guarded onlyOwner control: guarded_control, no inter-principal boundary, no bypass -> REJECT_CONFIRMED
    owner = {
        "proposed_reject_reason": "onlyOwner setter; owner is trusted",
        "relied_upon_invariant": "only the owner can call setConfig",
        "mechanism_class": "guarded_control", "inter_principal_trust_boundary": False,
        "counterexample_found": False,
    }
    chk(evaluate(owner).recommended_verdict == REJECT_CONFIRMED, "guarded onlyOwner control, no inter-principal boundary -> REJECT_CONFIRMED")

    # ---- supporting rules ----
    # counterexample claimed without a trace -> REOPEN
    cex_no_trace = dict(h01_local, counterexample_found=True, counterexample_trace="")
    chk(evaluate(cex_no_trace).recommended_verdict == REOPEN, "counterexample_found without trace -> REOPEN")
    # needs_execution + idea -> NEEDS_EXECUTION (orderings enumerated)
    needs_exec = dict(utr, needs_execution=True, execution_test_idea="Foundry: close market mid-batch, assert last user withdrawal short")
    chk(evaluate(needs_exec).recommended_verdict == NEEDS_EXECUTION, "needs_execution + test idea -> NEEDS_EXECUTION")
    # needs_execution without idea -> REOPEN
    needs_exec_noidea = dict(utr, needs_execution=True, execution_test_idea="")
    chk(evaluate(needs_exec_noidea).recommended_verdict == REOPEN, "needs_execution without idea -> REOPEN")
    # missing invariant -> REOPEN
    chk(evaluate({"mechanism_class": "accounting"}).recommended_verdict == REOPEN, "missing relied_upon_invariant -> REOPEN")
    # unresolved ordering dependency -> REOPEN
    unres = dict(utr, unresolved_ordering_dependency="whether closeMarket can run mid-batch is unclear")
    chk(evaluate(unres).recommended_verdict == REOPEN, "unresolved ordering dependency -> REOPEN")
    # 'other' mechanism with no counterexample and <3 orderings is NOT force-reopened (only the 4 classes require 3)
    other = {"relied_upon_invariant": "x", "mechanism_class": "other", "counterexample_found": False}
    chk(evaluate(other).recommended_verdict == REJECT_CONFIRMED, "'other' class (<3 orderings) not force-reopened -> REJECT_CONFIRMED")

    # advisory-only: result carries no severity field
    chk("severity" not in evaluate(utr)._asdict(), "result emits no severity field (advisory-only)")
    chk(FLAGS["is_gate"] is False and FLAGS["routes_in_production"] is False, "FLAGS un-wired (is_gate/routes_in_production false)")

    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--json", help="case JSON")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    c = json.loads(args.json) if args.json else {}
    print(json.dumps(evaluate(c)._asdict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
