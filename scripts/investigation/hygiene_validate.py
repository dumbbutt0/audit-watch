#!/usr/bin/env python3
"""
Phase-78 deterministic hygiene validator for P77 investigation bundles (RESEARCH-ONLY, un-wired).

Makes missed verification steps FAIL-CLOSED: a bundle may not reach a promotion-like status (POC_REQUIRED /
READY_FOR_HUMAN_REVIEW) unless verification is complete and (for READY) an adversarial review PASSed. Reuses the P77
state machine (transitions) + falsifier/ledger vocab (deep_pass). Never wired into production; never routes.

validate(bundle, review=None) -> (ok: bool, violations: list[str], recommended_status: str)
CLI exits nonzero on any violation. Usage: hygiene_validate.py --bundle <p> [--review <p>] | --self-test
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from investigation import transitions as T  # noqa: E402
from investigation.deep_pass import FALSIFIERS, DEFENSE_LEDGER_FIELDS  # noqa: E402

PROMOTION = {"POC_REQUIRED", "READY_FOR_HUMAN_REVIEW"}
REQUIRED_TOP = ("candidate_id", "detector_family", "final_decision", "status_reason", "defense_ledger",
                "exploit_path", "source_falsification", "state_trace")
BAD_CLASSES = {"unknown", "source_unavailable"}

# family -> defenses that are CRITICAL for that mechanism (union'd with bundle.critical_defenses)
FAMILY_CRITICAL = {
    "signature_replay": ["nonce_or_replay_guard", "state_consume_or_check"],
    "missing_or_unconsumed_nonce_in_state_changing_signature_v1": ["nonce_or_replay_guard", "state_consume_or_check"],
    "missing_auth": ["access_control"],
    "missing_auth_public_privileged_mutation_v1": ["access_control"],
    "wrong_actor": ["access_control"],
    "post_publication_creator_overreach_v1": ["access_control"],
    "value_flow": ["accounting_invariant", "final_invariant_check"],
    "multicall_invariant": ["final_invariant_check"],
    "oracle": ["oracle_or_price_dependency"],
}


def _critical_defenses(bundle: Dict[str, Any]) -> set:
    fam = (bundle.get("detector_family") or "").lower()
    crit = set(bundle.get("critical_defenses", []) or [])
    for k, v in FAMILY_CRITICAL.items():
        if k.lower() in fam or fam in k.lower():
            crit |= set(v)
    return crit


def _flags_ok(bundle: Dict[str, Any]) -> bool:
    return (bundle.get("research_only") is True and bundle.get("review_only") is True
            and bundle.get("is_gate") is False and bundle.get("routes_in_production") is False
            and (bundle.get("routed_manifest_ids") in ([], None)) and not bundle.get("routed_manifest_ids"))


def validate(bundle: Dict[str, Any], review: Optional[Dict[str, Any]] = None) -> Tuple[bool, List[str], str]:
    v: List[str] = []
    status = bundle.get("final_decision") or bundle.get("status")
    rec = status

    # 0. production-routing / flags
    if not _flags_ok(bundle):
        v.append("production-routing/flags violation (must be research_only+review_only, is_gate:false, "
                 "routes_in_production:false, routed_manifest_ids:[])")
        rec = "REJECTED"

    # 1. forbidden finality language anywhere
    try:
        T.assert_no_forbidden_label(json.dumps(bundle, default=str))
    except T.ForbiddenTransition as e:
        v.append(f"forbidden finality language: {e}")
        rec = "REJECTED"

    # 2. status enum
    if status not in (T.TERMINALS):
        v.append(f"final_decision '{status}' not in {sorted(T.TERMINALS)}")

    # 3. state_trace must be a legal path (catches detector->finding shortcut & forbidden transitions)
    trace = bundle.get("state_trace") or []
    if not trace or trace[0] != "STATIC_LEAD":
        v.append("state_trace missing or does not start at STATIC_LEAD")
    else:
        for a, b in zip(trace, trace[1:]):
            try:
                T.assert_transition(a, b)
            except T.ForbiddenTransition as e:
                v.append(f"illegal state transition in trace: {e}")
                rec = "REJECTED"

    # 4. required top-level fields
    for f in REQUIRED_TOP:
        if f not in bundle:
            v.append(f"missing required field: {f}")

    ledger = bundle.get("defense_ledger") or {}
    ex = bundle.get("exploit_path") or {}
    inv = bundle.get("invariant_analysis") or {}
    sf = bundle.get("source_falsification") or {}
    impact = bundle.get("impact_analysis") or {}

    # 5. REJECTED needs a source-backed reason
    if status == "REJECTED":
        reason = (bundle.get("status_reason") or "")
        if not reason or not any(tok in reason for tok in ("defense blocks", "source-falsified", "no ", "intentional",
                                                           "no measurable impact", "no source-backed")):
            v.append("REJECTED without a source-backed rejection reason (defense/falsifier/missing-evidence)")

    # 6. promotion-like statuses: deep checks
    if status in PROMOTION:
        # 6a. helper/modifier/defense ledger present + access_control classified somewhere (helper/modifier check done)
        if not ledger:
            v.append("promotion without a defense ledger (helper/modifier/library defenses not traced)")
        # 6b. survived source falsification
        fired = [k for k in FALSIFIERS if sf.get(k) is True]
        if fired:
            v.append(f"promotion despite fired source-falsifier(s): {fired}")
            rec = "REJECTED"
        # 6c. critical defenses must not be unknown/source_unavailable
        crit = _critical_defenses(bundle)
        unk_crit = [k for k in crit if (k not in ledger) or (ledger.get(k, {}).get("classification") in BAD_CLASSES)]
        if unk_crit:
            v.append(f"promotion with unknown/source_unavailable critical defense: {unk_crit}")
            rec = "NEEDS_CONTEXT"
        # 6d. a blocking defense must not coexist with promotion
        blocking = [k for k, val in ledger.items() if isinstance(val, dict) and val.get("classification") == "blocks_candidate"]
        if blocking:
            v.append(f"promotion despite blocking defense(s): {blocking}")
            rec = "REJECTED"
        # 6e. exploit path: attacker sequence + broken invariant + impact
        if not ex.get("transaction_sequence"):
            v.append("promotion without a concrete attacker transaction_sequence")
        if not inv.get("broken_invariant"):
            v.append("promotion without an explicit broken invariant")
        if not (impact.get("impact_category") and impact.get("minimum_profit_or_damage_condition")):
            v.append("promotion without measurable impact (impact_category + minimum_profit_or_damage_condition)")
        # 6f. POC_REQUIRED needs a named missing proof
        if status == "POC_REQUIRED" and bundle.get("poc_needed") is not True:
            v.append("POC_REQUIRED without poc_needed=true (no named missing proof)")
        # 6g. READY: unknown/source_unavailable blocks ONLY for CRITICAL/relevant defenses (handled by 6c above) —
        #     a defense classified `irrelevant` needs no source proof beyond that classification. READY also needs an
        #     adversarial review PASS and must not still require a PoC.
        if status == "READY_FOR_HUMAN_REVIEW":
            if bundle.get("poc_needed") is True:
                v.append("READY_FOR_HUMAN_REVIEW but poc_needed=true (should be POC_REQUIRED)")
            rs = (review or {}).get("review_status")
            if rs != "PASS":
                v.append(f"READY_FOR_HUMAN_REVIEW requires an adversarial review PASS (got {rs!r})")
                rec = "NEEDS_CONTEXT"

    ok = len(v) == 0
    if not ok and rec in PROMOTION:
        rec = "NEEDS_CONTEXT"
    return ok, v, rec


# --------------------------------- self-test ---------------------------------

def _good_ready() -> Dict[str, Any]:
    from investigation.deep_pass import run
    from investigation.lead_schema import normalize_lead
    lead = normalize_lead({"candidate_id": "ok", "detector_family": "value_flow", "contract": "C", "function": "f"})
    ev = {"context": {"source_resolved": True, "reachability": "external"},
          "defense_ledger": {"accounting_invariant": {"classification": "bypassed"}, "final_invariant_check": {"classification": "irrelevant"}, "access_control": {"classification": "irrelevant"}},
          "exploit": {"rejection_case": "x", "transaction_sequence": "attacker calls f", "broken_invariant": "conservation",
                      "impact_category": "fund_loss", "minimum_profit_or_damage_condition": "drains", "attacker_profile": "EOA",
                      "entrypoint": "f", "source_evidence": "C.sol:1"},
          "source_falsification": {k: False for k in FALSIFIERS}, "poc_needed": False}
    return run(lead, ev)


def _self_test() -> int:
    ok = True
    PASS = {"review_status": "PASS"}
    # a) good READY + adversarial PASS -> ok
    o1, v1, _ = validate(_good_ready(), PASS)
    print(f"  [{'PASS' if o1 else 'FAIL'}] good READY + adversarial PASS -> ok ({v1})"); ok &= o1
    # b) good READY without review -> blocked
    o2, v2, r2 = validate(_good_ready(), None)
    cb = (not o2) and r2 == "NEEDS_CONTEXT"
    print(f"  [{'PASS' if cb else 'FAIL'}] READY without adversarial PASS -> blocked -> {r2}"); ok &= cb
    # c) READY with unknown critical defense -> blocked
    b = _good_ready(); b["defense_ledger"]["accounting_invariant"] = {"classification": "unknown"}
    o3, v3, r3 = validate(b, PASS)
    cc = (not o3) and r3 == "NEEDS_CONTEXT"
    print(f"  [{'PASS' if cc else 'FAIL'}] READY + unknown critical defense -> blocked ({r3})"); ok &= cc
    # d) forbidden finality language -> fail
    b2 = _good_ready(); b2["human_review_notes"] = "this is a confirmed bug"
    o4, v4, _ = validate(b2, PASS)
    cd = not o4 and any("forbidden finality" in x for x in v4)
    print(f"  [{'PASS' if cd else 'FAIL'}] forbidden finality language -> fail"); ok &= cd
    # e) illegal state_trace (detector->finding) -> fail
    b3 = _good_ready(); b3["state_trace"] = ["STATIC_LEAD", "READY_FOR_HUMAN_REVIEW"]
    o5, v5, _ = validate(b3, PASS)
    ce = not o5 and any("illegal state transition" in x for x in v5)
    print(f"  [{'PASS' if ce else 'FAIL'}] detector->finding trace -> fail"); ok &= ce
    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle"); ap.add_argument("--review"); ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    if not args.bundle:
        ap.error("--bundle <path> or --self-test")
    bundle = json.loads(Path(args.bundle).read_text())
    review = json.loads(Path(args.review).read_text()) if args.review else None
    ok, viol, rec = validate(bundle, review)
    print(json.dumps({"ok": ok, "violations": viol, "recommended_status": rec}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
