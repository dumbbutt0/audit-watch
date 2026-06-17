#!/usr/bin/env python3
"""
Phase-78 missed-step review workflow — deterministic runner stub (RESEARCH-ONLY, un-wired).

No dynamic-workflow runtime exists in this repo, so the missed-step fan-out is implemented as a deterministic stub: given a
P77 bundle (+ optional adversarial review), it computes 5 isolated verifier roles and 1 synthesizer, returning a
promotion-safe decision. In real use the verifier roles are isolated agents driven by the two P78 skills; the stub encodes
the same fail-closed synthesis rules so the workflow is testable. Spec: documentation/workflows/candidate_missed_step_review.md.

Never wired into production; never routes. Usage: missed_step_workflow_stub.py --bundle <p> [--review <p>] | --self-test
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from investigation.deep_pass import FALSIFIERS  # noqa: E402
from investigation.hygiene_validate import validate, _critical_defenses, BAD_CLASSES, PROMOTION  # noqa: E402

PASS, FAIL, UNKNOWN = "PASS", "FAIL", "UNKNOWN"


def _verifier(name, status, evidence="", missed=None, blocking="", rec=None) -> Dict[str, Any]:
    return {"verifier_name": name, "status": status, "source_evidence": evidence,
            "missed_steps": missed or [], "blocking_reason": blocking, "recommended_status": rec}


def run_workflow(bundle: Dict[str, Any], review: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    ctx = bundle.get("context_summary") or {}
    ledger = bundle.get("defense_ledger") or {}
    ex = bundle.get("exploit_path") or {}
    inv = bundle.get("invariant_analysis") or {}
    impact = bundle.get("impact_analysis") or {}
    sf = bundle.get("source_falsification") or {}
    crit = _critical_defenses(bundle)

    verifiers: List[Dict[str, Any]] = []

    # A. Reachability Verifier
    if not ctx.get("source_resolved"):
        verifiers.append(_verifier("reachability", UNKNOWN, missed=["source/call-path not resolved"],
                                   blocking="source unresolved", rec="NEEDS_CONTEXT"))
    else:
        verifiers.append(_verifier("reachability", PASS, evidence=str(ctx.get("reachability"))))

    # B. Defense Ledger Verifier
    blocking = [k for k, val in ledger.items() if isinstance(val, dict) and val.get("classification") == "blocks_candidate"]
    unk_crit = [k for k in crit if (k not in ledger) or (ledger.get(k, {}).get("classification") in BAD_CLASSES)]
    if blocking:
        verifiers.append(_verifier("defense_ledger", FAIL, evidence=str({k: ledger[k] for k in blocking}),
                                   blocking="defense blocks candidate", rec="REJECTED"))
    elif unk_crit:
        verifiers.append(_verifier("defense_ledger", UNKNOWN, missed=[f"unclassified critical defense: {unk_crit}"],
                                   blocking="critical defense unknown", rec="NEEDS_CONTEXT"))
    elif not ledger:
        verifiers.append(_verifier("defense_ledger", UNKNOWN, missed=["no defense ledger"], blocking="no ledger", rec="NEEDS_CONTEXT"))
    else:
        verifiers.append(_verifier("defense_ledger", PASS))

    # C. Source Falsifier
    fired = [k for k in FALSIFIERS if sf.get(k) is True]
    if fired:
        verifiers.append(_verifier("source_falsifier", FAIL, evidence=str(fired), blocking="source-falsified", rec="REJECTED"))
    elif not sf:
        verifiers.append(_verifier("source_falsifier", UNKNOWN, missed=["source falsification not performed"], rec="NEEDS_CONTEXT"))
    else:
        verifiers.append(_verifier("source_falsifier", PASS))

    # D. Invariant & Impact Verifier
    missing = [k for k, present in (("broken_invariant", inv.get("broken_invariant")),
                                    ("transaction_sequence", ex.get("transaction_sequence")),
                                    ("impact", impact.get("impact_category"))) if not present]
    if missing:
        verifiers.append(_verifier("invariant_impact", FAIL, missed=missing, blocking="incomplete exploit/impact", rec="REJECTED"))
    else:
        verifiers.append(_verifier("invariant_impact", PASS))

    # E. Provenance & Transition Verifier (reuse the hygiene validator)
    ok, viol, hv_rec = validate(bundle, review)
    if ok:
        verifiers.append(_verifier("provenance_transition", PASS))
    else:
        prov_fail = any(("transition" in x or "routing" in x or "forbidden finality" in x) for x in viol)
        verifiers.append(_verifier("provenance_transition", FAIL if prov_fail else UNKNOWN,
                                   missed=viol, blocking="hygiene violations", rec=hv_rec))

    # F. Synthesizer (fail-closed)
    statuses = {v["status"] for v in verifiers}
    blocking_checks = [v["verifier_name"] for v in verifiers if v["status"] != PASS]
    missed = [m for v in verifiers for m in v["missed_steps"]]
    required_fixes = [f"{v['verifier_name']}: {v['blocking_reason']}" for v in verifiers if v["status"] != PASS and v["blocking_reason"]]

    claimed = bundle.get("final_decision")
    if any(v["status"] == FAIL and v["recommended_status"] == "REJECTED" for v in verifiers):
        final = "REJECTED"
    elif FAIL in statuses or UNKNOWN in statuses:
        final = "NEEDS_CONTEXT"
    else:
        # all PASS -> honor the claimed promotion terminal, but only if hygiene allowed it and (for READY) adversarial PASS
        if claimed == "READY_FOR_HUMAN_REVIEW" and (review or {}).get("review_status") != "PASS":
            final = "NEEDS_CONTEXT"; blocking_checks.append("adversarial_review"); required_fixes.append("adversarial_review: PASS required")
        elif claimed in PROMOTION:
            final = claimed
        else:
            final = claimed or "NEEDS_CONTEXT"

    promotion_allowed = final in PROMOTION
    return {"research_only": True, "review_only": True, "is_gate": False, "routes_in_production": False, "routed_manifest_ids": [],
            "candidate_id": bundle.get("candidate_id"), "verifiers": verifiers,
            "final_status": final, "blocking_checks": blocking_checks, "missed_steps": missed,
            "required_fixes": required_fixes, "promotion_allowed": promotion_allowed,
            "reason": "fail-closed synthesis of isolated verifier roles + hygiene validator + adversarial review"}


def _self_test() -> int:
    from investigation.hygiene_validate import _good_ready
    ok = True
    r1 = run_workflow(_good_ready(), {"review_status": "PASS"})
    c1 = r1["final_status"] == "READY_FOR_HUMAN_REVIEW" and r1["promotion_allowed"]
    print(f"  [{'PASS' if c1 else 'FAIL'}] clean bundle + adversarial PASS -> READY allowed ({r1['final_status']})"); ok &= c1
    r2 = run_workflow(_good_ready(), {"review_status": "UNKNOWN"})
    c2 = not r2["promotion_allowed"]
    print(f"  [{'PASS' if c2 else 'FAIL'}] adversarial UNKNOWN -> promotion blocked ({r2['final_status']})"); ok &= c2
    b = _good_ready(); b["source_falsification"]["impact_prevented_by_later_invariant"] = True
    r3 = run_workflow(b, {"review_status": "PASS"})
    c3 = r3["final_status"] == "REJECTED"
    print(f"  [{'PASS' if c3 else 'FAIL'}] falsifier fired -> REJECTED ({r3['final_status']})"); ok &= c3
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
    print(json.dumps(run_workflow(bundle, review), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
