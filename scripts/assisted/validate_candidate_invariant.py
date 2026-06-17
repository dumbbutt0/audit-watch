#!/usr/bin/env python3
"""
validate_candidate_invariant.py — P98 ASSISTED-MODE candidate validator (RESEARCH-ONLY, UN-WIRED).

P97 fired the stop condition for fully autonomous blind discovery: the system completed traces and ordering
checks but tested the WRONG invariant (invariant SELECTION is the capability boundary). P98 repositions
Audit-Watch as a human-in-the-loop VALIDATOR: a human / static tool / fuzzer supplies the candidate invariant
and its supporting evidence, and this script runs the PROVEN components in order and returns a reject-first
decision. It NEVER selects the invariant, NEVER sets production severity, NEVER auto-submits, NEVER routes.

Pipeline (reuses the existing checks unchanged; does NOT re-implement them):
  localized_depth_trace.evaluate  ->  adversarial_ordering_check.evaluate  ->  maximal_consequence_check.assess
    ->  hygiene_validate.validate  ->  severity_impact_gate.gate

Input: an assisted_candidate_intake JSON (schemas/assisted_candidate_intake.schema.json). `candidate_invariant`
is REQUIRED and non-empty. The intake MAY carry analyst-supplied evidence blocks consumed by the checks:
  depth_trace        -> the localized_depth_trace input (5-step trace + concrete_outcome)
  adversarial_ordering -> the adversarial_ordering_check input (invariant + orderings/counterexample)
  impact_assessment  -> {impact_class, proven_magnitude, source_true, material_consequence, ...} for
                        maximal_consequence_check + severity_impact_gate
Absent evidence is reject-first: you cannot reach VALIDATED_FOR_POC_HANDOFF without supplying it.

Output bundle (to --out): validation_report.md, trace.json, ordering_check.json, consequence_check.json,
severity_gate.json, decision.json.

Decision states: VALIDATED_FOR_POC_HANDOFF | REJECTED_SOURCE_PROVEN_SAFE | NEEDS_MORE_CONTEXT | NEEDS_EXECUTION |
BLOCKED_UNSUPPORTED_CLAIM | BLOCKED_SCOPE_OR_DUPLICATE_PENDING.

is_gate:false research_only:true review_only:true routes_in_production:false routed_manifest_ids:[].
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any, Dict, NamedTuple, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent.parent
import sys
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "investigation"))
from investigation import localized_depth_trace as DT       # noqa: E402
from investigation import adversarial_ordering_check as AO   # noqa: E402
from investigation import maximal_consequence_check as MC    # noqa: E402
from investigation import hygiene_validate as HV             # noqa: E402
from investigation import severity_impact_gate as SG         # noqa: E402

FLAGS = {"is_gate": False, "research_only": True, "review_only": True,
         "routes_in_production": False, "routed_manifest_ids": []}

VALIDATED = "VALIDATED_FOR_POC_HANDOFF"
REJECTED_SAFE = "REJECTED_SOURCE_PROVEN_SAFE"
NEEDS_CONTEXT = "NEEDS_MORE_CONTEXT"
NEEDS_EXECUTION = "NEEDS_EXECUTION"
BLOCKED_UNSUPPORTED = "BLOCKED_UNSUPPORTED_CLAIM"
BLOCKED_SCOPE_DUP = "BLOCKED_SCOPE_OR_DUPLICATE_PENDING"

DECISION_STATES = {VALIDATED, REJECTED_SAFE, NEEDS_CONTEXT, NEEDS_EXECUTION,
                   BLOCKED_UNSUPPORTED, BLOCKED_SCOPE_DUP}

_LEGAL_HYGIENE_TRACE = ["STATIC_LEAD", "CONTEXT_MAPPED", "DEFENSE_TRACED",
                        "EXPLOIT_PATH_ATTEMPTED", "IMPACT_CHECKED", "SOURCE_FALSIFIED", "POC_REQUIRED"]


class ValidationResult(NamedTuple):
    decision: str
    reason: str
    trace_result: Optional[Dict[str, Any]]
    ordering_result: Optional[Dict[str, Any]]
    consequence_result: Optional[Dict[str, Any]]
    hygiene_result: Optional[Dict[str, Any]]
    severity_result: Optional[Dict[str, Any]]


def _nonempty_str(v: Any) -> bool:
    return isinstance(v, str) and bool(v.strip())


def _build_hygiene_bundle(intake: Dict[str, Any], impact: Dict[str, Any]) -> Dict[str, Any]:
    """Assemble a hygiene bundle from the intake + supplied impact_assessment. POC_REQUIRED + poc_needed
    (the honest assisted-mode status: validated for handoff, no executable PoC yet)."""
    cid = f"{intake.get('contract')}.{intake.get('function')}"
    seq = intake.get("attacker_sequence") or [
        intake.get("entrypoint") or "EOA entrypoint",
        intake.get("suspected_break") or "invariant break",
        intake.get("expected_impact") or "impact realized",
    ]
    return {**FLAGS,
            "candidate_id": cid,
            "detector_family": "assisted_candidate",
            "final_decision": "POC_REQUIRED",
            "poc_needed": True,
            "status_reason": f"assisted candidate, source-backed: {intake.get('candidate_invariant')}",
            "state_trace": list(_LEGAL_HYGIENE_TRACE),
            "defense_ledger": intake.get("defense_ledger") or {"supplied_defense_review": {"classification": "irrelevant"}},
            "exploit_path": {"transaction_sequence": [s for s in seq if _nonempty_str(s)]},
            "invariant_analysis": {"broken_invariant": intake.get("candidate_invariant")},
            "impact_analysis": {
                "impact_category": impact.get("impact_category") or intake.get("expected_impact") or "impact",
                "minimum_profit_or_damage_condition": impact.get("minimum_profit_or_damage_condition")
                or intake.get("suspected_break") or "stated break condition",
            },
            "source_falsification": {}}


def validate(intake: Optional[Dict[str, Any]] = None) -> ValidationResult:
    """Run the assisted-mode validation pipeline (reject-first / default-deny)."""
    c = intake or {}

    # (0) load-bearing precondition: a non-empty candidate_invariant must be supplied.
    if not _nonempty_str(c.get("candidate_invariant")):
        return ValidationResult(BLOCKED_UNSUPPORTED,
                                "no candidate_invariant supplied — assisted-mode requires the invariant "
                                "(invariant selection is the capability boundary P97 exposed)",
                                None, None, None, None, None)

    requested = str(c.get("requested_check") or "VALIDATE").upper()

    # (1) TRIAGE — localized depth trace (requires a supplied trace block).
    trace_in = c.get("depth_trace")
    if not isinstance(trace_in, dict) or not trace_in:
        return ValidationResult(NEEDS_CONTEXT,
                                "no depth_trace evidence supplied — provide the 5-step localized trace "
                                "(localized_mechanism, controlled_inputs, pre_state, operation_trace, "
                                "boundary_cases, post_state, concrete_outcome)",
                                None, None, None, None, None)
    tr = DT.evaluate(trace_in)
    trd = tr._asdict()
    if tr.recommended_verdict in (DT.INSUFFICIENT, "NEEDS_CONTEXT"):
        return ValidationResult(NEEDS_CONTEXT,
                                f"depth trace -> {tr.recommended_verdict}: {tr.reasons[-1] if tr.reasons else ''}",
                                trd, None, None, None, None)

    if requested == "TRACE_ONLY":
        # report the trace verdict without promoting.
        if tr.recommended_verdict == "REJECT":
            return ValidationResult(REJECTED_SAFE, "TRACE_ONLY: depth trace REJECT (source-backed harmless/bounded)",
                                    trd, None, None, None, None)
        return ValidationResult(NEEDS_EXECUTION, "TRACE_ONLY: depth trace PASS — hand to STRESS/REPRODUCE next",
                                trd, None, None, None, None)

    # (2) STRESS — adversarial ordering / boundary enumeration (requires a supplied ordering block).
    ord_in = c.get("adversarial_ordering")
    if not isinstance(ord_in, dict) or not ord_in:
        return ValidationResult(NEEDS_CONTEXT,
                                "no adversarial_ordering evidence supplied — state relied_upon_invariant and "
                                "enumerate >=3 orderings (or a counterexample) before validating",
                                trd, None, None, None, None)
    ao = AO.evaluate(ord_in)
    aod = ao._asdict()
    if ao.recommended_verdict == AO.REOPEN:
        return ValidationResult(NEEDS_CONTEXT, f"adversarial ordering -> REOPEN_DEPTH_TRACE: {ao.reasons[-1] if ao.reasons else ''}",
                                trd, aod, None, None, None)
    if ao.recommended_verdict == AO.NEEDS_EXECUTION:
        return ValidationResult(NEEDS_EXECUTION, f"adversarial ordering -> NEEDS_EXECUTION: {ao.reasons[-1] if ao.reasons else ''}",
                                trd, aod, None, None, None)
    if ao.recommended_verdict == AO.REJECT_CONFIRMED:
        # a confirmed reject (depth REJECT or guarded) is a source-proven-safe negative — NOT a finding.
        return ValidationResult(REJECTED_SAFE,
                                "adversarial ordering -> REJECT_CONFIRMED: invariant holds across enumerated "
                                "orderings; source-proven safe (not a finding)",
                                trd, aod, None, None, None)
    # else PASS_CANDIDATE -> proceed to VERIFY.

    # (3) VERIFY — maximal consequence + severity gate + hygiene.
    impact = c.get("impact_assessment")
    if not isinstance(impact, dict) or not impact:
        return ValidationResult(NEEDS_CONTEXT,
                                "PASS_CANDIDATE but no impact_assessment supplied — provide impact_class + "
                                "proven_magnitude + source_true + material_consequence to gate severity",
                                trd, aod, None, None, None)
    cons = MC.assess(impact)
    consd = cons._asdict()
    # reject-first: an escalator asserted without source backing is an unsupported claim.
    if cons.attach_high_markers and not bool(impact.get("source_backed", impact.get("source_true", False))):
        return ValidationResult(BLOCKED_UNSUPPORTED,
                                "maximal_consequence: High escalator asserted without source backing (unsupported claim)",
                                trd, aod, consd, None, None)

    sgr = SG.gate(c.get("promotion_status", "POC_REQUIRED"), impact)
    sgd = sgr._asdict()
    if not sgr.kept:
        return ValidationResult(BLOCKED_UNSUPPORTED,
                                f"severity gate demoted/blocked the claim ({sgr.reason}) -> severity FP blocks handoff",
                                trd, aod, consd, None, sgd)

    hb = _build_hygiene_bundle(c, impact)
    ok, viol, rec = HV.validate(hb, review=c.get("adversarial_review"))
    hyd = {"hygiene_ok": ok, "violations": viol, "recommended": rec}
    if not ok:
        return ValidationResult(NEEDS_CONTEXT, f"hygiene not satisfied: {viol[0] if viol else 'unknown'}",
                                trd, aod, consd, hyd, sgd)

    # (4) human-final gates: scope/duplicate are PENDING until a human clears them.
    if requested == "SUBMISSION_PACKAGE":
        scope = str(c.get("scope_check_status") or "PENDING").upper()
        dup = str(c.get("duplicate_check_status") or "PENDING").upper()
        if scope != "IN_SCOPE" or dup not in ("CLEAR",):
            return ValidationResult(BLOCKED_SCOPE_DUP,
                                    f"submission package requested but scope={scope}/duplicate={dup} pending human review",
                                    trd, aod, consd, hyd, sgd)

    return ValidationResult(VALIDATED,
                            "PASS_CANDIDATE survived depth trace + adversarial ordering + maximal consequence "
                            "+ severity gate + hygiene — recommend PoC handoff (human-gated)",
                            trd, aod, consd, hyd, sgd)


# ----------------------------------------------------------------- bundle writer
def _report_md(intake: Dict[str, Any], res: ValidationResult) -> str:
    L = []
    L.append(f"# Assisted-mode validation — {intake.get('contract')}.{intake.get('function')}")
    L.append("")
    L.append("RESEARCH-ONLY · advisory · un-wired. Never sets severity, never auto-submits, never routes.")
    L.append("")
    L.append(f"- **subject:** {intake.get('subject')}  ·  **commit:** {intake.get('commit')}")
    L.append(f"- **supplied_by:** {intake.get('supplied_by')}  ·  **requested_check:** {intake.get('requested_check')}")
    L.append(f"- **candidate_invariant:** {intake.get('candidate_invariant')}")
    L.append(f"- **suspected_break:** {intake.get('suspected_break')}")
    L.append("")
    L.append(f"## DECISION: `{res.decision}`")
    L.append(f"{res.reason}")
    L.append("")
    def blk(title, d):
        if d is not None:
            L.append(f"### {title}")
            L.append("```json")
            L.append(json.dumps(d, indent=2))
            L.append("```")
    blk("localized_depth_trace", res.trace_result)
    blk("adversarial_ordering_check", res.ordering_result)
    blk("maximal_consequence_check", res.consequence_result)
    blk("severity_impact_gate", res.severity_result)
    blk("hygiene_validate", res.hygiene_result)
    L.append("")
    L.append("## Next (human)")
    if res.decision == VALIDATED:
        L.append("- Hand to PoC via `scripts/handoff_generator.py` (REPRODUCE). PoC handoff is human-gated; "
                 "no auto-submission.")
    elif res.decision in (NEEDS_CONTEXT, NEEDS_EXECUTION):
        L.append("- Supply the missing evidence / execution and re-run. Reject-first: not yet a finding.")
    elif res.decision == REJECTED_SAFE:
        L.append("- Source-proven safe across the enumerated orderings — not a finding. Re-open only with a "
                 "different invariant + a concrete counterexample.")
    else:
        L.append("- Blocked: resolve the unsupported claim / scope / duplicate before proceeding.")
    return "\n".join(L) + "\n"


def write_bundle(intake: Dict[str, Any], res: ValidationResult, out_dir: Path) -> Dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "trace.json": res.trace_result or {},
        "ordering_check.json": res.ordering_result or {},
        "consequence_check.json": res.consequence_result or {},
        "severity_gate.json": res.severity_result or {},
        "decision.json": {**FLAGS, "decision": res.decision, "reason": res.reason,
                          "candidate_id": f"{intake.get('contract')}.{intake.get('function')}",
                          "subject": intake.get("subject"), "supplied_by": intake.get("supplied_by"),
                          "requested_check": intake.get("requested_check"),
                          "candidate_invariant": intake.get("candidate_invariant")},
    }
    written = {}
    for name, data in files.items():
        p = out_dir / name
        p.write_text(json.dumps(data, indent=2))
        written[name] = str(p)
    rp = out_dir / "validation_report.md"
    rp.write_text(_report_md(intake, res))
    written["validation_report.md"] = str(rp)
    return written


def _self_test() -> int:
    ok = True
    def chk(cond, m):
        nonlocal ok; ok &= bool(cond); print(f"  [{'PASS' if cond else 'FAIL'}] {m}")

    inv = "a user cannot list/sell more than maxSellPercent of their original allocation"
    good_trace = {
        "localized_mechanism": "VestingManager.listVesting sellLimit vs maxSellPercent",
        "controlled_inputs": "EOA seller + sybil buyer; repeated list/buy cycles",
        "pre_state": "allocations[seller].sold/bought; original alloc",
        "operation_trace": "each purchase grows buyer.bought -> raises buyer.sellLimit; cycle re-lists",
        "boundary_cases": "after N cycles cumulative sold across cartel > maxSellPercent of original",
        "post_state": "cartel sells > cap; restriction defeated",
        "concrete_outcome": "PASS",
    }
    good_ord = {
        "relied_upon_invariant": inv, "mechanism_class": "accounting",
        "counterexample_found": True,
        "counterexample_trace": "buy-and-resell cycles inflate `bought`, raising sellLimit beyond the cap",
    }
    good_impact = {"impact_class": "medium", "proven_magnitude": "significant", "source_true": True,
                   "source_backed": True, "material_consequence": ["denial_of_asset_movement"]}

    # (0) no invariant -> BLOCKED_UNSUPPORTED
    chk(validate({"contract": "C", "function": "f"}).decision == BLOCKED_UNSUPPORTED,
        "missing candidate_invariant -> BLOCKED_UNSUPPORTED_CLAIM")
    # (1) no trace -> NEEDS_MORE_CONTEXT
    chk(validate({"candidate_invariant": inv}).decision == NEEDS_CONTEXT,
        "no depth_trace -> NEEDS_MORE_CONTEXT")
    # wrong-invariant rejection WITHOUT becoming a finding: depth REJECT + ordering REJECT_CONFIRMED
    reject_trace = dict(good_trace, concrete_outcome="REJECT",
                        boundary_cases="cap holds: moving tokens to sybil consumes seller cap",
                        post_state="no cap multiplication; conserves")
    reject_ord = {"relied_upon_invariant": "token sum is conserved", "mechanism_class": "accounting",
                  "ordering_cases_tested": ["list-then-buy", "claim-then-list", "sybil wash"],
                  "counterexample_found": False}
    r = validate({"candidate_invariant": "token sum conserved", "depth_trace": reject_trace,
                  "adversarial_ordering": reject_ord})
    chk(r.decision == REJECTED_SAFE, "depth REJECT + ordering REJECT_CONFIRMED -> REJECTED_SOURCE_PROVEN_SAFE (not a finding)")
    # full PASS_CANDIDATE path -> VALIDATED_FOR_POC_HANDOFF (only after all checks)
    v = validate({"candidate_invariant": inv, "depth_trace": good_trace, "adversarial_ordering": good_ord,
                  "impact_assessment": good_impact, "requested_check": "VALIDATE"})
    chk(v.decision == VALIDATED, "PASS_CANDIDATE + checks pass -> VALIDATED_FOR_POC_HANDOFF")
    # severity FP blocks handoff: dust impact demotes
    fp_impact = {"impact_class": "dust", "proven_magnitude": "transient", "source_true": True}
    f = validate({"candidate_invariant": inv, "depth_trace": good_trace, "adversarial_ordering": good_ord,
                  "impact_assessment": fp_impact})
    chk(f.decision == BLOCKED_UNSUPPORTED, "severity FP (dust) blocks handoff -> BLOCKED_UNSUPPORTED_CLAIM")
    # REOPEN ordering -> NEEDS_MORE_CONTEXT
    reopen_ord = {"relied_upon_invariant": inv, "mechanism_class": "accounting",
                  "ordering_cases_tested": ["one ordering"], "counterexample_found": False}
    ro = validate({"candidate_invariant": inv, "depth_trace": good_trace, "adversarial_ordering": reopen_ord,
                   "impact_assessment": good_impact})
    chk(ro.decision == NEEDS_CONTEXT, "ordering REOPEN (<3) -> NEEDS_MORE_CONTEXT")
    # NEEDS_EXECUTION passes through
    needs_exec_ord = dict(good_ord); needs_exec_ord.pop("counterexample_found"); needs_exec_ord.pop("counterexample_trace")
    needs_exec_ord.update({"ordering_cases_tested": ["a", "b", "c"], "needs_execution": True,
                           "execution_test_idea": "Foundry: N buy/sell cycles, assert cap exceeded"})
    ne = validate({"candidate_invariant": inv, "depth_trace": good_trace, "adversarial_ordering": needs_exec_ord,
                   "impact_assessment": good_impact})
    chk(ne.decision == NEEDS_EXECUTION, "ordering NEEDS_EXECUTION -> NEEDS_EXECUTION")
    # SUBMISSION_PACKAGE with pending scope/dup -> BLOCKED_SCOPE_OR_DUPLICATE_PENDING
    sp = validate({"candidate_invariant": inv, "depth_trace": good_trace, "adversarial_ordering": good_ord,
                   "impact_assessment": good_impact, "requested_check": "SUBMISSION_PACKAGE"})
    chk(sp.decision == BLOCKED_SCOPE_DUP, "SUBMISSION_PACKAGE + pending scope/dup -> BLOCKED_SCOPE_OR_DUPLICATE_PENDING")
    # TRACE_ONLY reports without promoting
    to = validate({"candidate_invariant": inv, "depth_trace": good_trace, "requested_check": "TRACE_ONLY"})
    chk(to.decision == NEEDS_EXECUTION, "TRACE_ONLY + PASS trace -> NEEDS_EXECUTION (no promotion)")
    chk(validate({"candidate_invariant": inv}).decision in DECISION_STATES, "decisions are in the enum")
    chk(FLAGS["is_gate"] is False and FLAGS["routes_in_production"] is False, "FLAGS un-wired")

    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--candidate", help="path to an assisted_candidate_intake JSON")
    ap.add_argument("--out", help="output bundle directory")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    if not args.candidate:
        ap.error("--candidate is required (or --self-test)")
    intake = json.loads(Path(args.candidate).read_text())
    res = validate(intake)
    if args.out:
        written = write_bundle(intake, res, Path(args.out))
        print(f"DECISION: {res.decision}")
        print(f"reason: {res.reason}")
        for name, p in written.items():
            print(f"  wrote {p}")
    else:
        print(json.dumps({"decision": res.decision, "reason": res.reason}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
