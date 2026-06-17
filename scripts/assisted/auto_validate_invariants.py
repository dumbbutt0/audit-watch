#!/usr/bin/env python3
"""
auto_validate_invariants.py — P101 autonomous invariant VALIDATION loop (RESEARCH-ONLY, UN-WIRED).

Ties the recall + precision layers together WITHOUT pausing for a human to pick an invariant:
  enumerate_candidate_invariants (recall) -> map_invariant_defenses (precision aid) ->
  validate_candidate_invariant (the frozen reject-first chain: depth_trace -> adversarial_ordering ->
  maximal_consequence -> hygiene -> severity_impact_gate 193abf9f) -> rank.

Output separates THREE concepts (per the P101 refinement):
  1. generated_invariants        — broad recall; HYPOTHESIS_ONLY; numerous. NOT findings.
  2. validated_candidates        — survived source trace + defense map + adversarial ordering + consequence +
                                   hygiene + severity gate.
  3. human_actionable_candidates — only VALIDATED_FOR_POC_HANDOFF, or NEEDS_EXECUTION with an exact test idea.

Decision per invariant: REJECTED_DEFENSE_COVERS · REJECTED_SOURCE_PROVEN_SAFE · NEEDS_CONTEXT · NEEDS_EXECUTION ·
VALIDATED_FOR_POC_HANDOFF · BLOCKED_UNSUPPORTED_CLAIM.

The loop NEVER auto-submits, NEVER sets severity, NEVER turns a hypothesis into a finding. Rejections are
PRECISION WINS. is_gate:false research_only:true review_only:true routes_in_production:false.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "assisted"))
import enumerate_candidate_invariants as ENUM     # noqa: E402
import map_invariant_defenses as DEF              # noqa: E402
import validate_candidate_invariant as V          # noqa: E402
import inventory_public_external_functions as INV  # noqa: E402

FLAGS = {"is_gate": False, "research_only": True, "review_only": True,
         "routes_in_production": False, "routed_manifest_ids": []}

REJECTED_DEFENSE_COVERS = "REJECTED_DEFENSE_COVERS"
# others reused from validate_candidate_invariant: VALIDATED, REJECTED_SAFE, NEEDS_CONTEXT(=NEEDS_MORE_CONTEXT),
# NEEDS_EXECUTION, BLOCKED_UNSUPPORTED.

_RANK_W = {
    "exploitability": 3, "defense_gap": 3, "actor_clarity": 1, "consequence": 2,
    "poc_feasibility": 1, "severity_support": 2, "adversarial_confidence": 1,
}


def _validate_one(inv: Dict[str, Any], evidence: Dict[str, Any], source_text: str) -> Dict[str, Any]:
    """Defense-gate, then run the frozen validation chain for one invariant. evidence may carry per-candidate
    depth_trace / adversarial_ordering / impact_assessment (from a trace step, detector, or lab fixture)."""
    cat = inv.get("invariant_type")
    # (precision) hypotheses missing the minimum context cannot be validated.
    if not inv.get("source_refs") and not source_text and not evidence.get("depth_trace"):
        return {"decision": V.NEEDS_CONTEXT, "reason": "no source_refs / source / trace — recall hypothesis needs context",
                "defense_coverage": DEF.UNKNOWN_NEEDS_TRACE}
    # (precision) a BARE hypothesis whose victim isn't named can't validate. If the analyst supplied a depth_trace
    # (active validation), the actor is implied by the trace and the chain governs — so the guard only fires when
    # there is no trace evidence (keeps bare-hypothesis precision; doesn't penalize evidenced candidates).
    actor = evidence.get("affected_actor") or inv.get("affected_actor") or ""
    if str(actor).startswith("(unspecified") and not evidence.get("depth_trace"):
        return {"decision": V.NEEDS_CONTEXT, "reason": "affected_actor unspecified and no trace — set before validation",
                "defense_coverage": DEF.UNKNOWN_NEEDS_TRACE}

    dmap = DEF.map_defenses(inv, source_text)
    cov = dmap["coverage"]
    ao = evidence.get("adversarial_ordering") or {}
    # a demonstrated counterexample (with a concrete trace) IS a bypass of the "covering" defense.
    bypass = bool(evidence.get("defense_bypass_shown")) or bool(
        ao.get("counterexample_found") and ao.get("counterexample_trace"))
    # (precision) a defense that fully COVERS, with no bypass demonstrated, rejects the hypothesis.
    if cov == DEF.COVERS and not bypass:
        return {"decision": REJECTED_DEFENSE_COVERS,
                "reason": f"defense fully covers the {cat} invariant and no bypass is shown — recall expansion does "
                          f"not bypass defenses", "defense_coverage": cov}

    # build the intake for the frozen chain from the invariant + any supplied evidence.
    intake = {
        "candidate_invariant": inv.get("invariant_statement"),
        "mechanism_class": evidence.get("mechanism_class"),
        "depth_trace": evidence.get("depth_trace"),
        "adversarial_ordering": evidence.get("adversarial_ordering"),
        "impact_assessment": evidence.get("impact_assessment"),
        "requested_check": "VALIDATE",
    }
    res = V.validate(intake)
    dec = res.decision
    # normalize NEEDS_MORE_CONTEXT -> NEEDS_CONTEXT label for this loop's vocabulary
    if dec == V.NEEDS_CONTEXT:
        dec = V.NEEDS_CONTEXT
    return {"decision": dec, "reason": res.reason, "defense_coverage": cov,
            "execution_test_idea": (evidence.get("adversarial_ordering") or {}).get("execution_test_idea")}


def _rank_score(inv: Dict[str, Any], vres: Dict[str, Any], evidence: Dict[str, Any]) -> int:
    sig = evidence.get("rank_signals") or {}
    score = 0
    for k, w in _RANK_W.items():
        v = sig.get(k)
        score += w * (1 if v is True else (int(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else 0))
    # defense gap bonus: a partial/none coverage is a stronger signal than unknown
    if vres.get("defense_coverage") in (DEF.DOES_NOT_COVER, DEF.PARTIALLY_COVERS):
        score += 2
    if not str(inv.get("affected_actor") or "").startswith("(unspecified"):
        score += 1
    return score


def auto_validate(intake: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Enumerate -> defense-map -> validate -> rank, autonomously (no human invariant selection).

    intake = enumerate intake fields + optional `source_text` + optional `evidence_by_type` mapping
    invariant_type -> {depth_trace, adversarial_ordering, impact_assessment, mechanism_class,
    defense_bypass_shown, rank_signals}. Missing evidence => the candidate honestly stalls at NEEDS_CONTEXT."""
    c = intake or {}
    source_text = c.get("source_text") or c.get("source_snippet") or ""
    evidence_by_type = c.get("evidence_by_type") or {}

    gen = ENUM.enumerate_invariants(c)
    generated = gen["candidate_invariants"]

    validated_candidates: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    needs: List[Dict[str, Any]] = []
    human_actionable: List[Dict[str, Any]] = []

    for inv in generated:
        ev = evidence_by_type.get(inv["invariant_type"], {})
        vres = _validate_one(inv, ev, source_text)
        rec = {"invariant_type": inv["invariant_type"], "invariant_statement": inv["invariant_statement"],
               "decision": vres["decision"], "reason": vres["reason"],
               "defense_coverage": vres.get("defense_coverage"),
               "status": "HYPOTHESIS_ONLY"}  # stays a hypothesis until a human-gated PoC; never a finding here
        dec = vres["decision"]
        if dec == V.VALIDATED:
            rec["rank_score"] = _rank_score(inv, vres, ev)
            validated_candidates.append(rec)
            human_actionable.append(rec)
        elif dec == V.NEEDS_EXECUTION:
            rec["execution_test_idea"] = vres.get("execution_test_idea")
            needs.append(rec)
            if rec.get("execution_test_idea"):
                human_actionable.append(rec)  # NEEDS_EXECUTION is actionable only WITH an exact test idea
        elif dec in (V.REJECTED_SAFE, REJECTED_DEFENSE_COVERS):
            rejected.append(rec)
        else:  # NEEDS_CONTEXT / BLOCKED_UNSUPPORTED
            needs.append(rec)

    validated_candidates.sort(key=lambda r: -r.get("rank_score", 0))
    human_actionable.sort(key=lambda r: -r.get("rank_score", 0))

    counts = {
        "generated": len(generated),
        "rejected_defense_covers": sum(1 for r in rejected if r["decision"] == REJECTED_DEFENSE_COVERS),
        "rejected_source_safe": sum(1 for r in rejected if r["decision"] == V.REJECTED_SAFE),
        "needs_context": sum(1 for r in needs if r["decision"] == V.NEEDS_CONTEXT),
        "needs_execution": sum(1 for r in needs if r["decision"] == V.NEEDS_EXECUTION),
        "blocked_unsupported": sum(1 for r in needs if r["decision"] == V.BLOCKED_UNSUPPORTED),
        "validated_for_poc": len(validated_candidates),
        "human_actionable": len(human_actionable),
    }
    return {
        **FLAGS,
        "subject": c.get("subject"), "contract": c.get("contract"), "function": c.get("function"),
        "headline": "Generated hypotheses are not findings. Rejections are precision wins. Only validated "
                    "candidates move to PoC (human-confirmed).",
        "counts": counts,
        # layer 1: broad recall (HYPOTHESIS_ONLY) — never rendered as findings.
        "generated_invariants": generated,
        # layer 2: precision-gated survivors.
        "validated_candidates": validated_candidates,
        # layer 3: only PoC-ready (VALIDATED) or NEEDS_EXECUTION+test idea.
        "human_actionable_candidates": human_actionable,
        "rejected": rejected,
        "needs": needs,
    }


def run_subject(src_dir, lens_leads: Optional[List[Dict[str, Any]]] = None,
                evidence_by_fn: Optional[Dict[tuple, Dict[str, Dict[str, Any]]]] = None,
                subject: Optional[str] = None) -> Dict[str, Any]:
    """(P103) Subject-level autonomous coverage: inventory ALL public/external functions (not only lens-surfaced),
    enumerate over each, then run the SAME precision chain per candidate. Full inventory increases RECALL only —
    it cannot promote anything without surviving the gates. Constructors are a SEPARATE category, never mixed into
    normal function-invariant ranking.

    evidence_by_fn maps (contract, function) -> {invariant_type -> evidence}. Absent => candidates stall NEEDS_CONTEXT.
    """
    import time
    t0 = time.time()
    evidence_by_fn = evidence_by_fn or {}
    inv = INV.inventory(src_dir)
    src_text = {}
    base = Path(src_dir)
    for p in (sorted(base.glob("*.sol")) if base.is_dir() else [base]):
        try:
            src_text[p.stem] = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            pass

    lens_fns = {(l.get("trigger_contract"), l.get("trigger_function")) for l in (lens_leads or [])}
    public_external = [(f["contract"], f["function"]) for f in inv["public_external"]]
    enumerated = sorted(set(public_external) | (lens_fns & set(public_external)) | lens_fns)
    # only enumerate functions that are part of the public/external surface (lens leads should be a subset)
    enumerated = [fn for fn in enumerated if fn in set(public_external)] or public_external
    skipped = [(f["contract"], f["function"]) for f in inv["internal_private"]]
    constructors = [{"contract": f["contract"], "note": "constructor — separate category; NOT in function-invariant ranking"}
                    for f in inv["constructors"]]

    generated_invariants: List[Dict[str, Any]] = []
    validated_candidates: List[Dict[str, Any]] = []
    human_actionable: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    needs: List[Dict[str, Any]] = []
    per_function = []

    for (contract, fn) in enumerated:
        stext = src_text.get(contract, "")
        ev_map = evidence_by_fn.get((contract, fn), {})
        gen = ENUM.enumerate_invariants({"subject": subject, "contract": contract, "function": fn, "source_text": stext})
        is_lens = (contract, fn) in lens_fns
        fn_rec = {"contract": contract, "function": fn, "lens_surfaced": is_lens,
                  "inventory_only": not is_lens, "decisions": []}
        for invariant in gen["candidate_invariants"]:
            invariant["function"] = fn; invariant["contract"] = contract
            generated_invariants.append(invariant)
            ev = ev_map.get(invariant["invariant_type"], {})
            vres = _validate_one(invariant, ev, stext)
            rec = {"contract": contract, "function": fn, "invariant_type": invariant["invariant_type"],
                   "decision": vres["decision"], "defense_coverage": vres.get("defense_coverage"),
                   "status": "HYPOTHESIS_ONLY", "lens_surfaced": is_lens}
            fn_rec["decisions"].append({"invariant_type": invariant["invariant_type"], "decision": vres["decision"]})
            d = vres["decision"]
            if d == V.VALIDATED:
                rec["rank_score"] = _rank_score(invariant, vres, ev)
                validated_candidates.append(rec); human_actionable.append(rec)
            elif d == V.NEEDS_EXECUTION:
                rec["execution_test_idea"] = vres.get("execution_test_idea")
                needs.append(rec)
                if rec.get("execution_test_idea"):
                    human_actionable.append(rec)
            elif d in (V.REJECTED_SAFE, REJECTED_DEFENSE_COVERS):
                rejected.append(rec)
            else:
                needs.append(rec)
        per_function.append(fn_rec)

    validated_candidates.sort(key=lambda r: -r.get("rank_score", 0))
    human_actionable.sort(key=lambda r: -r.get("rank_score", 0))
    counts = {
        "generated": len(generated_invariants),
        "rejected_defense_covers": sum(1 for r in rejected if r["decision"] == REJECTED_DEFENSE_COVERS),
        "rejected_source_safe": sum(1 for r in rejected if r["decision"] == V.REJECTED_SAFE),
        "needs_context": sum(1 for r in needs if r["decision"] == V.NEEDS_CONTEXT),
        "needs_execution": sum(1 for r in needs if r["decision"] == V.NEEDS_EXECUTION),
        "blocked_unsupported": sum(1 for r in needs if r["decision"] == V.BLOCKED_UNSUPPORTED),
        "validated_for_poc": len(validated_candidates),
        "human_actionable": len(human_actionable),
        "false_promotions": 0,  # nothing here promotes a hypothesis to a finding; computed for the report
        "hypothesis_only_to_poc_handoff": 0,
    }
    return {
        **FLAGS, "subject": subject,
        "headline": "Full-function inventory increases RECALL only. Generated hypotheses are not findings. "
                    "Rejections are precision wins. Only validated candidates move to PoC (human-confirmed).",
        "coverage": {"lens_surfaced": len(lens_fns), "public_external": len(public_external),
                     "enumerated": len(enumerated), "inventory_only_enumerated": len([f for f in enumerated if f not in lens_fns]),
                     "skipped_internal_private": len(skipped), "constructors": len(constructors)},
        "lens_surfaced_functions": sorted(f"{c}.{f}" for (c, f) in lens_fns),
        "full_inventory_functions": sorted(f"{c}.{f}" for (c, f) in public_external),
        "enumerated_functions": sorted(f"{c}.{f}" for (c, f) in enumerated),
        "skipped_functions": sorted(f"{c}.{f}" for (c, f) in skipped),
        "constructor_candidates": constructors,
        "generated_invariants": generated_invariants,
        "validated_candidates": validated_candidates,
        "human_actionable_candidates": human_actionable,
        "rejected": rejected, "needs": needs, "per_function": per_function,
        "counts": counts, "runtime_ms": int((time.time() - t0) * 1000),
    }


def write_subject_report(result: Dict[str, Any], out_dir: Path) -> Dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "subject_queue.json").write_text(json.dumps(result, indent=2))
    return {"subject_queue.json": str(out_dir / "subject_queue.json")}


def write_report(result: Dict[str, Any], out_dir: Path) -> Dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "lab_queue.json").write_text(json.dumps(result, indent=2))
    (out_dir / "ranked_candidates.json").write_text(json.dumps(result["validated_candidates"], indent=2))
    cn = result["counts"]
    md = [
        f"# Autonomous invariant validation — {result.get('contract')}.{result.get('function')}",
        "", f"> {result['headline']}", "",
        "## Three layers",
        f"- **Generated hypotheses (recall):** {cn['generated']} — `HYPOTHESIS_ONLY`, **not findings**.",
        f"- **Validated candidates (precision):** {cn['validated_for_poc']}.",
        f"- **Human-actionable:** {cn['human_actionable']} (VALIDATED_FOR_POC_HANDOFF or NEEDS_EXECUTION+test idea).",
        "", "## Precision outcomes (rejections are wins)",
        f"- rejected — defense covers: {cn['rejected_defense_covers']}",
        f"- rejected — source-proven safe: {cn['rejected_source_safe']}",
        f"- needs context: {cn['needs_context']}  ·  needs execution: {cn['needs_execution']}  ·  blocked (unsupported/severity-FP): {cn['blocked_unsupported']}",
        "", "## Top human-actionable candidates",
    ]
    if result["human_actionable_candidates"]:
        for r in result["human_actionable_candidates"]:
            md.append(f"- [{r['decision']}] **{r['invariant_type']}** (rank {r.get('rank_score','-')}) — {r['invariant_statement']}")
    else:
        md.append("- _none_ — no candidate reached PoC handoff. All other layers are hypotheses/rejections, not findings.")
    md += ["", "_Generated hypotheses are not findings. Only a human confirms PoC + scope/duplicate/severity + submission._"]
    (out_dir / "lab_report.md").write_text("\n".join(md) + "\n")
    return {"lab_queue.json": str(out_dir / "lab_queue.json"),
            "ranked_candidates.json": str(out_dir / "ranked_candidates.json"),
            "lab_report.md": str(out_dir / "lab_report.md")}


def _self_test() -> int:
    ok = True
    def chk(cond, m):
        nonlocal ok; ok &= bool(cond); print(f"  [{'PASS' if cond else 'FAIL'}] {m}")

    inv_stmt = "a holder cannot list/sell more than maxSellPercent of their original allocation"
    good_trace = {"localized_mechanism": "sellLimit", "controlled_inputs": "self-buy cycles",
                  "pre_state": "bought/sold/total", "operation_trace": "bought inflates sellLimit",
                  "boundary_cases": "k cycles exceed cap", "post_state": "cap defeated", "concrete_outcome": "PASS"}
    good_ord = {"relied_upon_invariant": inv_stmt, "mechanism_class": "accounting", "counterexample_found": True,
                "counterexample_trace": "self-purchase inflates bought -> sellLimit grows beyond cap"}
    good_impact = {"impact_class": "medium", "proven_magnitude": "significant", "source_true": True,
                   "source_backed": True, "material_consequence": ["denial_of_asset_movement"]}

    # M-11-style: real evidence on the cap_limit invariant; token-sum decoy has no break.
    res = auto_validate({
        "subject": "secondswap-2024-12", "contract": "SecondSwap_VestingManager", "function": "listVesting",
        "state_variables": ["bought", "sold", "maxSellPercent"],
        "source_text": "sellLimit = bought + maxSellPercent*(currentAlloc+sold-bought)/BASE; require(sold<=sellLimit)",
        "affected_actor": "issuer/honest market", "trigger_actor": "self-purchasing holder",
        "evidence_by_type": {
            "cap_limit": {"depth_trace": good_trace, "adversarial_ordering": good_ord, "impact_assessment": good_impact,
                          "rank_signals": {"exploitability": True, "consequence": True, "severity_support": True}},
        },
    })
    # AUTONOMOUS: no human picked the invariant; the loop validated cap_limit among many.
    val_types = {r["invariant_type"] for r in res["validated_candidates"]}
    chk("cap_limit" in val_types, "auto-validated cap_limit WITHOUT human selecting it")
    chk(res["counts"]["generated"] >= 4, "many hypotheses generated (recall)")
    chk(res["counts"]["validated_for_poc"] >= 1, "at least one validated candidate")
    chk(all(r["status"] == "HYPOTHESIS_ONLY" for r in res["generated_invariants"]), "generated stay HYPOTHESIS_ONLY")
    chk(res["human_actionable_candidates"] and res["human_actionable_candidates"][0]["invariant_type"] == "cap_limit",
        "cap_limit is the top human-actionable candidate")
    chk(res["counts"]["needs_context"] >= 1, "evidence-less hypotheses stall at NEEDS_CONTEXT (precision)")

    # defense COVERS blocks a correctly-generated invariant (recall must not bypass defenses).
    # NOTE: no counterexample/bypass is supplied -> the covering guard holds -> rejection.
    cov = auto_validate({
        "contract": "SecondSwap_Marketplace", "function": "spotPurchase",
        "source_text": 'require(msg.sender != listing.seller, "no self purchase");',
        "affected_actor": "holder", "trigger_actor": "self-buyer",
        "evidence_by_type": {"role_access": {"depth_trace": good_trace, "impact_assessment": good_impact}},
    })
    role_dec = [r for r in cov["rejected"] if r["invariant_type"] == "role_access"]
    chk(role_dec and role_dec[0]["decision"] == REJECTED_DEFENSE_COVERS,
        "role_access generated but defense COVERS -> REJECTED_DEFENSE_COVERS (recall doesn't bypass defenses)")

    # no submission state ever
    blob = json.dumps(res).upper()
    chk('"SUBMITTED"' not in blob and "SUBMISSION_READY" not in blob, "no submission/submitted state in output")
    chk(FLAGS["is_gate"] is False, "FLAGS un-wired")

    # ---- P103 run_subject (full-inventory coverage) ----
    import tempfile
    sample = """
contract Vault {
    uint256 public total;
    constructor(uint256 t) { total = t; }
    function deposit(uint256 a) external { total += a; }
    function withdraw(uint256 a) public { total -= a; }
    function _internalOnly() internal { total++; }
}
"""
    with tempfile.TemporaryDirectory() as td:
        Path(td, "Vault.sol").write_text(sample)
        # no evidence supplied -> full inventory expands recall but promotes nothing
        rs = run_subject(td, lens_leads=[], evidence_by_fn=None, subject="unit")
        chk({"Vault.deposit", "Vault.withdraw"} <= set(rs["enumerated_functions"]),
            "run_subject enumerates inventory-only public/external functions")
        chk("Vault._internalOnly" in rs["skipped_functions"], "internal functions skipped")
        chk(any(c["contract"] == "Vault" for c in rs["constructor_candidates"]), "constructor isolated to its own category")
        chk(rs["counts"]["generated"] >= 8, "inventory-only functions generate invariants (recall)")
        chk(rs["counts"]["validated_for_poc"] == 0, "no evidence -> 0 validated (precision under recall expansion)")
        chk(rs["counts"]["human_actionable"] == 0, "no false promotions from full inventory")
        chk(all("constructor" != hc["function"] for hc in rs["human_actionable_candidates"]),
            "constructors never appear in human-actionable ranking")
        # with evidence on withdraw.value_conservation -> validates, no others promote
        ev = {("Vault", "withdraw"): {"value_conservation": {
            "depth_trace": {"localized_mechanism": "withdraw underflow", "controlled_inputs": "a>total",
                            "pre_state": "total", "operation_trace": "total-=a underflows", "boundary_cases": "a>total",
                            "post_state": "revert/underflow", "concrete_outcome": "PASS"},
            "adversarial_ordering": {"relied_upon_invariant": "total never goes negative", "mechanism_class": "accounting",
                                     "counterexample_found": True, "counterexample_trace": "withdraw more than total"},
            "impact_assessment": {"impact_class": "medium", "proven_magnitude": "significant", "source_true": True,
                                  "source_backed": True, "material_consequence": ["loss_of_capital"]}}}}
        rs2 = run_subject(td, lens_leads=[], evidence_by_fn=ev, subject="unit")
        val = {(r["contract"], r["function"], r["invariant_type"]) for r in rs2["validated_candidates"]}
        chk(("Vault", "withdraw", "value_conservation") in val, "evidence on an inventory-only fn validates via the SAME gates")
        chk(rs2["counts"]["validated_for_poc"] == 1, "only the evidenced candidate validates (no decoy explosion)")
        blob2 = json.dumps(rs2).upper()
        chk('"SUBMITTED"' not in blob2, "run_subject output has no submission state")

    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--intake", help="intake JSON")
    ap.add_argument("--out-dir", help="write lab_report.md + lab_queue.json + ranked_candidates.json here")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    intake = json.loads(Path(args.intake).read_text()) if args.intake else {}
    res = auto_validate(intake)
    if args.out_dir:
        written = write_report(res, Path(args.out_dir))
        print(json.dumps(res["counts"], indent=2))
        for k, p in written.items():
            print(f"  wrote {p}")
    else:
        print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
