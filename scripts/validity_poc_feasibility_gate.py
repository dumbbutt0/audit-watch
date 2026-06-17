#!/usr/bin/env python3
"""validity_poc_feasibility_gate.py — Phase-27 RESEARCH-ONLY validity / PoC-feasibility PRE-gate.

Sits BETWEEN discovery and the impact-direction gate:
    located finding -> [validity gate] -> impact-direction gate -> report candidate
It answers "is this actually worth impact-direction analysis?" and STOPS invalid-but-well-structured findings
before the impact-direction gate can assign a confident family/polarity (the Phase-26 hallucination). It does NOT
improve discovery; it only prevents non-bugs from becoming confident directions.

ENGINE, NOT LOOKUP: decisions derive ONLY from OBJECTIVE bundle facts; a bundle MUST NOT carry answer-key fields
(awarded / expected_* / known_bug / contest_result / report_id) — rejected by schema validator. Missing facts =>
NEEDS_PROOF; never fabricate. Lineage: evidence_bundle_gate (completeness) + confirm_reachability (reachability).

  is_gate:false  research_only:true  routes_in_production:false  routed_manifest_ids:[]  human_approval_required:true
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

FLAGS = {"is_gate": False, "research_only": True, "routes_in_production": False, "routed_manifest_ids": []}
FORBIDDEN_INPUT = {"awarded", "expected_decision", "expected_severity", "known_bug", "contest_result", "report_id",
                   "awarded_severity", "awarded_id", "expected"}
HARMFUL = {"fund_loss", "fund_freeze", "dos", "accounting_corruption", "reward_extraction", "liveness_failure",
           "governance_takeover"}
# privileged paths that still admit an attacker-relevant route
ATTACKER_RELEVANT_PRIV = {"compromised_role", "misconfigured_authority", "public_initializer", "signer_confusion",
                          "privileged_fn_via_untrusted_caller"}
DECISION_PRECEDENCE = ["REJECT_QA_LOW", "REJECT_NOT_REACHABLE", "REJECT_NO_CONCRETE_IMPACT", "NEEDS_PROOF",
                       "PASS_TO_IMPACT_GATE"]


class BundleValidationError(Exception):
    pass


def assert_no_answer_fields(b, path="bundle"):
    """Reject any answer-key-like field anywhere in the input bundle (no answer smuggling)."""
    if isinstance(b, dict):
        bad = FORBIDDEN_INPUT & set(b.keys())
        if bad:
            raise BundleValidationError(f"answer-key field(s) in input {path}: {sorted(bad)}")
        for k, v in b.items():
            assert_no_answer_fields(v, f"{path}.{k}")
    elif isinstance(b, list):
        for i, v in enumerate(b):
            assert_no_answer_fields(v, f"{path}[{i}]")


def _ne(x):
    return bool(x) and (not isinstance(x, (list, dict, str)) or len(x) > 0)


def run(bundle):
    assert_no_answer_fields(bundle)
    r = bundle.get("reachability", {}) or {}
    ac = bundle.get("attacker_control", {}) or {}
    ss = bundle.get("state_setup", {}) or {}
    iv = bundle.get("invariant_violation", {}) or {}
    oc = bundle.get("observable_consequence", {}) or {}
    sk = (bundle.get("minimal_exploit_sketch", {}) or {}).get("steps") or []
    nc = bundle.get("negative_control", {}) or {}
    ev = bundle.get("evidence", {}) or {}
    burden = (bundle.get("proof_burden") or "medium").lower()

    priv = (r.get("actor_privilege") or "permissionless").lower()
    attacker_relevant = bool(r.get("attacker_relevant_path")) or (r.get("attacker_relevant_kind") in ATTACKER_RELEVANT_PRIV)

    checks, fails = {}, []  # fails: (reason_code, note)

    # 1 reachability (privileged not auto-rejected; needs an attacker-relevant route)
    if not r.get("reachable"):
        checks["reachability"] = False; fails.append(("REJECT_NOT_REACHABLE", "path not reachable"))
    elif priv in ("privileged", "admin") and not attacker_relevant:
        checks["reachability"] = False
        fails.append(("REJECT_NOT_REACHABLE", f"{priv}-only with no attacker-relevant path"))
    else:
        checks["reachability"] = True

    # 2 attacker/relevant-actor control
    checks["attacker_control"] = _ne(ac.get("controlled_inputs")) or _ne(ac.get("controlled_state")) or attacker_relevant
    if not checks["attacker_control"]:
        fails.append(("NEEDS_PROOF", "no attacker-controlled input/state"))

    # 3 concrete state preconditions
    checks["state_setup"] = _ne(ss.get("preconditions"))
    if not checks["state_setup"]:
        fails.append(("NEEDS_PROOF", "no concrete state preconditions"))

    # 4 invariant violation
    checks["invariant_violation"] = _ne(iv.get("invariant")) and _ne(iv.get("how_violated"))
    if not checks["invariant_violation"]:
        fails.append(("REJECT_NO_CONCRETE_IMPACT", "no named invariant violation"))

    # 5 harmful observable consequence
    checks["observable_consequence"] = (oc.get("consequence_type") in HARMFUL) and _ne(oc.get("on_chain_delta"))
    if not checks["observable_consequence"]:
        fails.append(("REJECT_NO_CONCRETE_IMPACT",
                      f"no harmful observable consequence (type={oc.get('consequence_type')})"))

    # 6 minimal exploit sketch
    checks["minimal_exploit_sketch"] = _ne(sk)
    if not checks["minimal_exploit_sketch"]:
        fails.append(("NEEDS_PROOF", "no minimal exploit sketch"))

    # 7 negative control (NOT a QA/config edge, with a reason)
    checks["negative_control"] = (nc.get("is_qa_or_config_edge") is False) and _ne(nc.get("why_not_qa"))
    if not checks["negative_control"]:
        fails.append(("REJECT_QA_LOW", "QA/config edge or no why_not_qa rationale"))

    # 8 evidence completeness
    checks["evidence_completeness"] = _ne(ev.get("source_spans")) and _ne(ev.get("call_path")) and _ne(ev.get("state_vars"))
    if not checks["evidence_completeness"]:
        fails.append(("NEEDS_PROOF", "incomplete source/call/state evidence"))

    # 7' proof burden: high burden needs strong sketch + full evidence, else NEEDS_PROOF
    strong = checks["minimal_exploit_sketch"] and checks["evidence_completeness"] and len(sk) >= 2
    if burden == "high" and not strong:
        fails.append(("NEEDS_PROOF", "high proof_burden without strong sketch+evidence"))

    # decision = earliest-strongest reason among fails; PASS only if none
    if not fails:
        decision, primary, secondary = "PASS_TO_IMPACT_GATE", None, []
    else:
        order = {c: i for i, c in enumerate(DECISION_PRECEDENCE)}
        primary_code = min((c for c, _ in fails), key=lambda c: order.get(c, 99))
        decision = primary_code
        primary = next(n for c, n in fails if c == primary_code)
        secondary = [f"{c}: {n}" for c, n in fails if not (c == primary_code and n == primary)]

    body = {**FLAGS, "tool": "validity_poc_feasibility_gate.py", "hypothesis_status": "HYPOTHESIS_UNCONFIRMED",
            "human_approval_required": True, "candidate_id": bundle.get("candidate_id"),
            "contract": bundle.get("contract"), "function": bundle.get("function"),
            "decision": decision, "primary_reason": primary, "secondary_reasons": secondary,
            "proof_burden": burden, "check_results": checks,
            "pass_to_impact_gate": decision == "PASS_TO_IMPACT_GATE"}
    blob = json.dumps(body).lower()
    for bad in ("confirmed", "proven", "exploitable", "valid bug", "submit", "guaranteed"):
        if re.search(r"\b" + re.escape(bad) + r"\b", blob):
            raise SystemExit(f"[validity_gate] verdict word '{bad}' leaked")
    return body


# ----------------------------- self-test -----------------------------

def _full_positive(**ov):
    b = {"candidate_id": "pos", "contract": "C", "function": "f",
         "reachability": {"reachable": True, "actor_privilege": "permissionless", "entrypoint": "f"},
         "attacker_control": {"controlled_inputs": ["x"], "controlled_state": []},
         "state_setup": {"preconditions": ["vault open"]},
         "invariant_violation": {"invariant": "supply==debt", "how_violated": "x bypasses check"},
         "observable_consequence": {"consequence_type": "fund_loss", "on_chain_delta": "attacker balance +N"},
         "minimal_exploit_sketch": {"steps": ["call f(x)", "withdraw"]},
         "negative_control": {"is_qa_or_config_edge": False, "why_not_qa": "drains real funds, not a config edge"},
         "evidence": {"source_spans": ["C.sol:10"], "call_path": ["f->_g"], "state_vars": ["bal"]},
         "proof_burden": "low"}
    b.update(ov); return b


def _self_test():
    ok = True
    cases = []

    # positive: all 8 present -> PASS
    cases.append(("positive all-8", _full_positive(), "PASS_TO_IMPACT_GATE"))

    # negative: Predy QA — no concrete consequence, no sketch, QA edge
    cases.append(("predy QA (P26 hallucination)", _full_positive(
        observable_consequence={"consequence_type": "none", "on_chain_delta": ""},
        minimal_exploit_sketch={"steps": []},
        negative_control={"is_qa_or_config_edge": True, "why_not_qa": ""},
        invariant_violation={"invariant": "", "how_violated": ""}), "REJECT_QA_LOW"))

    # negative: Decent collectFees Low-only QA replay
    cases.append(("decent collectFees QA", _full_positive(
        negative_control={"is_qa_or_config_edge": True, "why_not_qa": ""}), "REJECT_QA_LOW"))

    # negative: Kleidi M-01 economic — reachable, real, but no concrete code-level sketch (economic)
    cases.append(("kleidi M-01 economic", _full_positive(
        consequence_ok=None,
        minimal_exploit_sketch={"steps": ["spam proposals"]},  # 1 step, economic
        proof_burden="high",
        observable_consequence={"consequence_type": "dos", "on_chain_delta": "victim gas drained"}), "NEEDS_PROOF"))

    # config-edge regression: reachable + sketch but NO harmful consequence + QA edge -> must NOT pass
    cases.append(("config-edge (reachable+sketch, harmless)", _full_positive(
        observable_consequence={"consequence_type": "config_edge", "on_chain_delta": ""},
        negative_control={"is_qa_or_config_edge": True, "why_not_qa": ""}), "REJECT_QA_LOW"))

    # not-reachable
    cases.append(("not reachable", _full_positive(
        reachability={"reachable": False, "actor_privilege": "permissionless", "entrypoint": "f"}),
        "REJECT_NOT_REACHABLE"))

    # privileged WITH attacker-relevant path -> NOT over-rejected (public initializer)
    cases.append(("privileged + public_initializer (not over-rejected)", _full_positive(
        reachability={"reachable": True, "actor_privilege": "admin", "entrypoint": "init",
                      "attacker_relevant_kind": "public_initializer"}), "PASS_TO_IMPACT_GATE"))

    # privileged WITHOUT attacker-relevant path -> reject
    cases.append(("privileged-only no attacker path", _full_positive(
        reachability={"reachable": True, "actor_privilege": "admin", "entrypoint": "setX"}),
        "REJECT_NOT_REACHABLE"))

    # missing evidence -> NEEDS_PROOF
    cases.append(("missing evidence", _full_positive(
        evidence={"source_spans": [], "call_path": [], "state_vars": []}), "NEEDS_PROOF"))

    for label, b, exp in cases:
        d = run(b)["decision"]
        good = d == exp
        ok &= good
        print(f"  [{'PASS' if good else 'FAIL'}] {label}: {d}  (expect {exp})")

    # forbidden-field validator
    try:
        run(_full_positive(awarded=True)); raised = False
    except BundleValidationError:
        raised = True
    print(f"  [{'PASS' if raised else 'FAIL'}] forbidden-field 'awarded' rejected by validator")
    ok &= raised

    # multi-reason: Predy QA records secondary reasons
    body = run(cases[1][1])
    multi = len(body["secondary_reasons"]) >= 1
    print(f"  [{'PASS' if multi else 'FAIL'}] negative records secondary reasons: {body['secondary_reasons'][:2]}")
    ok &= multi

    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle")
    ap.add_argument("--out")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    if not args.bundle:
        ap.error("--bundle or --self-test required")
    body = run(json.load(open(args.bundle)))
    out = args.out or Path(args.bundle).with_name(Path(args.bundle).stem + "_validity.json")
    Path(out).write_text(json.dumps(body, indent=2))
    print(f"[validity_gate] {body['decision']} -> {out}  (primary: {body['primary_reason']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
