#!/usr/bin/env python3
"""
Phase-77 Universal Candidate Deep-Pass runner (RESEARCH-ONLY, REVIEW-ONLY, un-wired).

Walks a normalized STATIC_LEAD through the enforced state machine
  STATIC_LEAD -> CONTEXT_MAPPED -> DEFENSE_TRACED -> EXPLOIT_PATH_ATTEMPTED -> IMPACT_CHECKED -> SOURCE_FALSIFIED
  -> {REJECTED | NEEDS_CONTEXT | POC_REQUIRED | READY_FOR_HUMAN_REVIEW}
applying reject-first discipline at every stage over an evidence dict (filled by an in-session agent / the existing
candidate gates in real use; by fixtures in tests). Produces an investigation BUNDLE, never a finding. Every progression is
checked by transitions.assert_transition so no shortcut (e.g. STATIC_LEAD -> READY_FOR_HUMAN_REVIEW) is possible.

POC_REQUIRED = permission to create a LOCAL PoC task only. READY_FOR_HUMAN_REVIEW = bundle ready for human review, NOT
submission-ready. Forbidden labels (confirmed bug / valid finding / submission ready) are never emitted.

is_gate:false research_only:true review_only:true routes_in_production:false routed_manifest_ids:[]. Never calls a
production gate; never routes.
Usage: deep_pass.py --self-test
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from investigation import transitions as T  # noqa: E402
from investigation.lead_schema import FLAGS, normalize_lead, is_valid_lead, RoutedSourceRefused  # noqa: E402

DEFENSE_LEDGER_FIELDS = (
    "access_control", "pause_guard", "reentrancy_guard", "nonce_or_replay_guard", "state_consume_or_check",
    "accounting_invariant", "slippage_or_price_bound", "caps_or_limits", "final_invariant_check",
    "role_or_admin_escape_hatch", "external_dependency", "oracle_or_price_dependency", "user_controlled_inputs",
    "cross_contract_assumptions", "upgradeability_or_owner_controls", "time_or_deadline_checks",
)
DEFENSE_CLASSES = ("blocks_candidate", "partially_covers_candidate", "irrelevant", "bypassed", "unknown", "source_unavailable")
FALSIFIERS = (
    "code_not_reachable", "caller_actually_authorized", "state_not_mutable", "missing_check_present_in_helper",
    "impact_prevented_by_later_invariant", "behavior_intentional_by_design", "hash_or_value_bound_to_mutable_state",
    "detector_name_confusion", "relies_on_out_of_scope_or_unavailable_source", "exploit_economically_meaningless",
)


def run(lead: Dict[str, Any], evidence: Dict[str, Any]) -> Dict[str, Any]:
    """Deterministic deep-pass. `lead` = normalized STATIC_LEAD; `evidence` = investigation inputs (agent/gates/fixtures)."""
    if not is_valid_lead(lead):
        raise ValueError("invalid STATIC_LEAD (must be normalized, non-routed, with candidate_id+detector_family)")
    evidence = evidence or {}
    state = "STATIC_LEAD"
    trace = [state]

    def to(nxt: str) -> None:
        nonlocal state
        T.assert_transition(state, nxt)  # raises on any forbidden transition
        state = nxt
        trace.append(nxt)

    def bundle(final: str, reason: str, **extra) -> Dict[str, Any]:
        to(final)  # validated terminal transition
        T.assert_no_forbidden_label(reason)
        ex = evidence.get("exploit", {}) or {}
        b = {**FLAGS,
             "candidate_id": lead.get("candidate_id"), "detector_family": lead.get("detector_family"),
             "status": final, "status_reason": reason,
             "trigger_summary": {"contract": lead.get("trigger_contract"), "function": lead.get("trigger_function"),
                                 "lines": lead.get("trigger_lines"), "suspicious_pattern": lead.get("suspicious_pattern"),
                                 "detector_claim": lead.get("detector_claim")},
             "context_summary": evidence.get("context", {}),
             "attacker_reachability": evidence.get("context", {}).get("reachability"),
             "defense_ledger": evidence.get("defense_ledger", {}),
             "invariant_analysis": {"broken_invariant": ex.get("broken_invariant"), "why_defenses_do_not_block": ex.get("why_existing_defenses_do_not_block")},
             "exploit_path": {k: ex.get(k) for k in ("attacker_profile", "entrypoint", "preconditions", "transaction_sequence", "state_before", "state_after", "rejection_case", "source_evidence")},
             "impact_analysis": {"impact_category": ex.get("impact_category"), "minimum_profit_or_damage_condition": ex.get("minimum_profit_or_damage_condition")},
             "source_falsification": evidence.get("source_falsification", {}),
             "missing_context": extra.get("missing_context"),
             "poc_needed": bool(evidence.get("poc_needed", True)) if final in ("POC_REQUIRED", "READY_FOR_HUMAN_REVIEW") else None,
             "human_review_notes": extra.get("human_review_notes"),
             "state_trace": trace,
             "final_decision": final}
        return b

    # ---- 1. CONTEXT_MAPPED (source resolved + reachable + context) ----
    ctx = evidence.get("context", {}) or {}
    if not ctx.get("source_available", True) or not ctx.get("source_resolved"):
        return bundle("NEEDS_CONTEXT", "source/call-path/context not resolved (source_resolved=%s available=%s)"
                      % (ctx.get("source_resolved"), ctx.get("source_available", True)),
                      missing_context="resolve source snippet+lines+hash, caller surface, related state")
    to("CONTEXT_MAPPED")

    # ---- 2. DEFENSE_TRACED (reject-first on a blocking defense; needs-context on unknown critical defense) ----
    ledger = evidence.get("defense_ledger", {}) or {}
    to("DEFENSE_TRACED")
    blocking = [k for k, v in ledger.items() if isinstance(v, dict) and v.get("classification") == "blocks_candidate"]
    if blocking:
        return bundle("REJECTED", "defense blocks candidate: " + ", ".join(
            f"{k} [{ledger[k].get('evidence') or ledger[k].get('refs')}]" for k in blocking))
    critical = set(evidence.get("critical_defenses", []) or [])
    unknown_crit = [k for k in critical if (k not in ledger) or (ledger.get(k, {}).get("classification") in ("unknown", "source_unavailable"))]
    if unknown_crit:
        return bundle("NEEDS_CONTEXT", "critical defense unknown/source-unavailable: " + ", ".join(unknown_crit),
                      missing_context="resolve the classification (with source) of: " + ", ".join(unknown_crit))

    # ---- 3. EXPLOIT_PATH_ATTEMPTED (reject-first: rejection_case required; then attacker path + broken invariant) ----
    ex = evidence.get("exploit", {}) or {}
    to("EXPLOIT_PATH_ATTEMPTED")
    if not ex.get("rejection_case"):
        return bundle("NEEDS_CONTEXT", "reject-first analysis not performed (no rejection_case written)",
                      missing_context="write the strongest source-backed rejection case before any promotion")
    if not ex.get("transaction_sequence") or not ex.get("broken_invariant"):
        return bundle("REJECTED", "no source-backed attacker sequence and/or no broken invariant identified")

    # ---- 4. IMPACT_CHECKED ----
    to("IMPACT_CHECKED")
    if not ex.get("impact_category") or not ex.get("minimum_profit_or_damage_condition"):
        return bundle("REJECTED", "no measurable impact (impact_category / minimum_profit_or_damage_condition absent)")

    # ---- 5. SOURCE_FALSIFIED (any falsifier True => candidate disproven) ----
    to("SOURCE_FALSIFIED")
    sf = evidence.get("source_falsification", {}) or {}
    fired = [k for k in FALSIFIERS if sf.get(k) is True]
    if fired:
        return bundle("REJECTED", "source-falsified: " + ", ".join(fired))

    # ---- 6. survived falsification -> promotion terminal (still not a verdict) ----
    if evidence.get("poc_needed", True):
        return bundle("POC_REQUIRED", "survived source falsification with a concrete attacker path; local PoC/fork proof "
                      "required before human promotion (POC_REQUIRED = local PoC-task permission only)",
                      human_review_notes="not a severity/validity/submission verdict")
    return bundle("READY_FOR_HUMAN_REVIEW", "source-backed attacker path + broken invariant + defense ledger + impact + "
                  "source-falsification pass; investigation bundle ready for a human to review (not a submission verdict)",
                  human_review_notes="human decides next step; not a submission verdict")


def write_bundle(bundle: Dict[str, Any], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / "bundle.json"
    p.write_text(json.dumps(bundle, indent=2))
    return p


# --------------------------------- self-test ---------------------------------

def _self_test() -> int:
    from investigation.lead_schema import normalize_lead as nl
    ok = True

    def lead(cid, fam="missing_auth"):
        return nl({"candidate_id": cid, "detector_family": fam, "contract": "C", "function": "f", "snippet": "..."})

    # a) defense blocks -> REJECTED
    a = run(lead("a"), {"context": {"source_resolved": True, "reachability": "external"},
                        "defense_ledger": {"access_control": {"classification": "blocks_candidate", "evidence": "onlyOwner modifier reachable"}}})
    ca = a["final_decision"] == "REJECTED"
    print(f"  [{'PASS' if ca else 'FAIL'}] defense blocks -> REJECTED ({a['final_decision']})"); ok &= ca
    # b) unknown critical defense -> NEEDS_CONTEXT
    b = run(lead("b"), {"context": {"source_resolved": True}, "critical_defenses": ["nonce_or_replay_guard"],
                        "defense_ledger": {"nonce_or_replay_guard": {"classification": "unknown"}}})
    cb = b["final_decision"] == "NEEDS_CONTEXT"
    print(f"  [{'PASS' if cb else 'FAIL'}] unknown critical defense -> NEEDS_CONTEXT ({b['final_decision']})"); ok &= cb
    # c) full survive, poc_needed -> POC_REQUIRED
    full_ex = {"rejection_case": "tried: caller is attacker-controlled, no modifier, state mutable",
               "transaction_sequence": "attacker calls f(...)", "broken_invariant": "X must hold",
               "impact_category": "fund_loss", "minimum_profit_or_damage_condition": "drain on each call",
               "attacker_profile": "EOA", "entrypoint": "f", "source_evidence": "C.sol:10-20"}
    c = run(lead("c"), {"context": {"source_resolved": True}, "defense_ledger": {"access_control": {"classification": "irrelevant"}},
                        "exploit": full_ex, "source_falsification": {k: False for k in FALSIFIERS}, "poc_needed": True})
    cc = c["final_decision"] == "POC_REQUIRED"
    print(f"  [{'PASS' if cc else 'FAIL'}] survive + poc_needed -> POC_REQUIRED ({c['final_decision']})"); ok &= cc
    # d) full survive, poc_not_needed -> READY_FOR_HUMAN_REVIEW
    d = run(lead("d"), {"context": {"source_resolved": True}, "defense_ledger": {"access_control": {"classification": "bypassed"}},
                        "exploit": full_ex, "source_falsification": {k: False for k in FALSIFIERS}, "poc_needed": False})
    cd = d["final_decision"] == "READY_FOR_HUMAN_REVIEW"
    print(f"  [{'PASS' if cd else 'FAIL'}] survive + !poc_needed -> READY_FOR_HUMAN_REVIEW ({d['final_decision']})"); ok &= cd
    # e) falsifier fired -> REJECTED
    e = run(lead("e"), {"context": {"source_resolved": True}, "defense_ledger": {"access_control": {"classification": "irrelevant"}},
                        "exploit": full_ex, "source_falsification": {**{k: False for k in FALSIFIERS}, "missing_check_present_in_helper": True}})
    ce = e["final_decision"] == "REJECTED" and "missing_check_present_in_helper" in e["status_reason"]
    print(f"  [{'PASS' if ce else 'FAIL'}] falsifier fired -> REJECTED ({e['final_decision']})"); ok &= ce
    # f) forbidden shortcut raises
    try:
        T.assert_transition("STATIC_LEAD", "READY_FOR_HUMAN_REVIEW"); cf = False
    except T.ForbiddenTransition:
        cf = True
    print(f"  [{'PASS' if cf else 'FAIL'}] STATIC_LEAD -> READY_FOR_HUMAN_REVIEW raises ({cf})"); ok &= cf
    # g) routed source refused
    try:
        normalize_lead({"candidate_id": "x", "detector_family": "y", "routes_in_production": True}); cg = False
    except RoutedSourceRefused:
        cg = True
    print(f"  [{'PASS' if cg else 'FAIL'}] routed source refused ({cg})"); ok &= cg
    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    ap.error("--self-test only (library used by the investigation deep-pass runner / tests)")


if __name__ == "__main__":
    raise SystemExit(main())
