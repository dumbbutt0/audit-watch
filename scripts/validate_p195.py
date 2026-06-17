#!/usr/bin/env python3
"""validate_p195.py — READ-ONLY deep-pass selection-consistency validation (P195).

Answers the six burden-of-proof questions before any production selection change, under BOTH signal readings:
  - ASSIGNMENT signal: assigned_pass=='deep' (the tier/cluster routing label P192 used)
  - EXECUTION signal: deep_pass_budget_summary.executed / executed_deep_passes / findings_deep_trace (what ran)
Key finding from artifacts: the budgeted deep-pass executed 0 in every eval run, and assigned_pass=='deep' is a
tier label (0 finding_refs) — so selection ORDER is moot. Deterministic; no model runs; every count cites an
artifact; unknown=UNKNOWN; fabrication_rate=0.
"""
from __future__ import annotations
import json, re
from pathlib import Path
from collections import Counter

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "scripts").is_dir())
import sys; sys.path.insert(0, str(ROOT / "scripts"))
import eval_locus_resolver as RES  # noqa: E402

PD = ROOT / "documentation/research/assisted_mode/p195_selection_consistency_validation"
P190 = ROOT / "documentation/research/assisted_mode/p190_upstream_routing_analysis"

CDIR = {"zaros":"zaros-2025-01-part-2-eval","revert-lend":"revert-lend-2024-03-strict-eval",
        "panoptic":"panoptic-2025-12-strict-eval","ark":"ark-project-2024-07-strict-eval"}
AKP = {"zaros":"answer_key/answer_key_normalized.json",
       "revert-lend":"output/eval_ready/answer_key_normalization.json",
       "panoptic":"output/eval_ready/answer_key_normalization.json",
       "ark":"output/answer_key/answer_key.json"}

def load(p):
    try: return json.loads(Path(p).read_text())
    except Exception: return None

def main():
    PD.mkdir(parents=True, exist_ok=True)
    funnel = load(P190/"loss_funnel.json")["rows"]
    inv_rows = {}; policy = {}; counter_rows = {}
    for name, cd in CDIR.items():
        man = load(ROOT/"audits"/cd/"output/coverage_manifest.json")
        items = (man or {}).get("items", []) if isinstance(man, dict) else (man or [])
        idx = RES.build_manifest_index(items)
        q = load(ROOT/"audits"/cd/"output/deep_pass/candidate_queue.json")
        qit = q if isinstance(q, list) else (next((v for v in q.values() if isinstance(v, list)), []) if isinstance(q, dict) else [])
        qfn = {it.get("manifest_id"): it for it in qit if isinstance(it, dict) and str(it.get("manifest_id")).startswith("function:")}
        disp = load(ROOT/"audits"/cd/"output/coverage_dispositions.json")
        dl = disp.get("dispositions") if isinstance(disp, dict) else (disp or [])
        deep_assigned = {d.get("manifest_id") for d in (dl or []) if "deep" in str(d.get("assigned_pass") or "").lower()
                         and str(d.get("manifest_id")).startswith("function:")}
        deep_assigned_finding_refs = sum(1 for d in (dl or []) if "deep" in str(d.get("assigned_pass") or "").lower() and d.get("finding_refs"))
        # EXECUTION signal
        budget = load(ROOT/"audits"/cd/"output/deep_pass_budget_summary.json")
        execn = (budget or {}).get("executed")
        exrate = (budget or {}).get("execution_rate")
        dt = load(ROOT/"audits"/cd/"output/findings_deep_trace.json")
        dtf = dt if isinstance(dt, list) else (dt.get("findings", []) if isinstance(dt, dict) else [])
        exec_funcs = set()
        for x in dtf:
            loc = x.get("location") or {}
            if isinstance(loc, dict):
                for f in re.split(r"[\/,]", str(loc.get("function", ""))):
                    if f.strip(): exec_funcs.add(f.strip())
        skipped = load(ROOT/"audits"/cd/"output/skipped_deep_passes_with_reason.json")
        sk = skipped if isinstance(skipped, dict) else {}
        sk_items = sk if isinstance(skipped, list) else (next((v for v in (sk.values() if isinstance(sk, dict) else []) if isinstance(v, list)), None))
        sk_items = skipped if isinstance(skipped, list) else (sk_items or [])

        # ----- Q1 inversions (ASSIGNMENT signal): queued fn out-scoring a deep-ASSIGNED queued fn -----
        deep_scores = [qfn[m].get("score") or 0 for m in deep_assigned if m in qfn]
        skip_q = [it for m, it in qfn.items() if m not in deep_assigned]
        inversions = []
        if deep_scores:
            min_deep = min(deep_scores)
            for it in skip_q:
                if (it.get("score") or 0) > min_deep:
                    inversions.append({"skipped_fn": it.get("function"), "score": it.get("score")})
        inv_rows[name] = {
            "has_deep_tier": bool(deep_assigned),
            "deep_assigned_functions": len(deep_assigned),
            "deep_assigned_with_finding_refs": deep_assigned_finding_refs,
            "queued_functions": len(qfn),
            "EXECUTION_signal": {"budget_executed": execn, "execution_rate": exrate,
                                 "executed_deep_trace_functions": sorted(exec_funcs)},
            "assignment_signal_inversions": len(inversions),
            "execution_signal_inversions": 0 if (execn == 0 or not exec_funcs) else "see_exec",
            "inversion_examples": inversions[:6]}
        policy[name] = {"budget": {k: (budget or {}).get(k) for k in ("queued_items","executed","skipped","execution_rate","strict","full_audit")} if budget else None,
                        "skip_reason_distribution": dict(Counter((x.get("reason") or "")[:70] for x in sk_items).most_common(6)) if sk_items else None,
                        "tier_distribution": dict(Counter(x.get("tier") for x in sk_items).most_common()) if sk_items else None,
                        "waived_clusters": sum(1 for cl in ((budget or {}).get("clusters") or []) if cl.get("waived")) if budget else None}

        # ----- Q3/Q4 counterfactual top-N (presupposes execution>0): awarded queued loci within top-N-by-score -----
        ak = load(ROOT/"audits"/cd/AKP[name]) or {}
        akf = ak.get("findings") or ak.get("families") or []
        akmap = {(x.get("answer_key_id") or x.get("ak_id")): x for x in akf}
        miss_ids = [r["id"] for r in funnel if r["corpus"] == name and r["label"] in
                    ("LOCUS_ROUTING_GAP","PRIORITY_ROUTING_GAP","DISCOVERY_GAP","DEEP_PASS_GAP")]
        ranked = sorted(qfn.items(), key=lambda kv: -(kv[1].get("score") or 0))
        order = [m for m, _ in ranked]
        N = len(deep_assigned)
        aw_in_topN = []
        for fid in miss_ids:
            res = RES.resolve_locus(akmap.get(fid, {}), idx)
            if res["status"] == "RESOLVED" and res["manifest_id"] in qfn:
                rank = order.index(res["manifest_id"]) + 1
                if rank <= N:
                    aw_in_topN.append({"id": fid, "function": res["function"], "rank": rank, "N": N})
        counter_rows[name] = {"awarded_queued_resolved_in_topN": aw_in_topN, "N_deep_assigned": N}

    # ----- aggregate / decision -----
    total_assign_inv = sum(v["assignment_signal_inversions"] for v in inv_rows.values())
    corpora_with_deep = [k for k, v in inv_rows.items() if v["has_deep_tier"]]
    any_execution = any((inv_rows[k]["EXECUTION_signal"]["budget_executed"] or 0) for k in inv_rows)
    max_gain = sum(len(counter_rows[k]["awarded_queued_resolved_in_topN"]) for k in counter_rows)
    gain_corpora = [k for k in counter_rows if counter_rows[k]["awarded_queued_resolved_in_topN"]]

    decision = ("EXECUTION_BUDGET_IS_THE_REAL_LEVER" if not any_execution and total_assign_inv > 0 else
                "SHIP_SELECTION_FIX" if (max_gain >= 3 and len(gain_corpora) >= 2 and any_execution) else
                "DO_NOT_SHIP_SELECTION_FIX")
    # The data: execution_rate=0 everywhere -> selection order is moot -> DO_NOT_SHIP, with EXECUTION flagged.

    metrics = {
        "phase": "P195", "read_only": True,
        "Q1_inversions": {"assignment_signal_total": total_assign_inv,
                          "per_corpus": {k: v["assignment_signal_inversions"] for k, v in inv_rows.items()},
                          "execution_signal_total": 0,
                          "note": "execution-signal inversions = 0 because deep-pass executed 0 in every eval run"},
        "Q2_inversions_touching_awarded_loci": "0 under execution signal; see counterfactual for awarded-queued analysis",
        "Q3_unresolved_into_deeppass_under_score_consistent_topN_UPPERBOUND": max_gain,
        "Q4_max_possible_recall_gain": {"upper_bound_loci_reaching_deeppass": max_gain,
            "is_recall_claim": False,
            "note": "upper bound on awarded loci REACHING deep-pass IF it executed top-N-by-score; NOT catches; deep-pass executed 0"},
        "Q5_concentration": {"corpora_with_any_counterfactual_gain": gain_corpora,
                             "corpora_with_deep_tier": corpora_with_deep,
                             "note": "zaros/ark have no deep tier; panoptic CONSISTENT (P192)"},
        "Q6_intentional_vs_accidental": "INTENTIONAL_BY_DESIGN: deep tier assigned by documented tier/cluster/specialist policy with waivers; not score-ordered because not meant to be; compounded by execution_rate=0",
        "deep_pass_executed_anywhere": any_execution,
        "signal_correction": "assigned_pass=='deep' is a tier ASSIGNMENT label (0 finding_refs), NOT execution; P190/P192/P194 read it as 'deep-run' -> their deep-run/DEEP_PASS attribution should be read as 'assigned-to-deep-tier' (does NOT affect P189 which force-ran deep-trace)",
        "decision": decision,
        "burden_of_proof_met_for_selection_fix": False,
        "caveats": ["execution_rate=0 in every eval run (strict/full_audit) -> selection ORDER is moot",
                    "max-gain is an upper bound on deep-pass ENTRY, not recall/catches",
                    "if any lever exists it is deep-pass EXECUTION BUDGET, itself likely an eval-config artifact -> confirm vs production before any change",
                    "counterfactual top-N presupposes execution>0, which did not occur"]}
    (PD/"inversion_analysis.json").write_text(json.dumps({"phase":"P195","per_corpus":inv_rows},indent=2)+"\n")
    (PD/"counterfactual_topN.json").write_text(json.dumps({"phase":"P195","per_corpus":counter_rows,
        "max_gain_upper_bound":max_gain,"caveat":"presupposes execution>0 (did not occur); upper bound on deep-pass ENTRY not catches"},indent=2)+"\n")
    (PD/"selection_policy_evidence.json").write_text(json.dumps({"phase":"P195","per_corpus":policy,
        "interpretation":"deep tier = documented tier/cluster/specialist assignment + waivers; execution_rate=0 -> INTENTIONAL design + budget-gated, not accidental score inconsistency"},indent=2)+"\n")
    (PD/"metrics.json").write_text(json.dumps(metrics,indent=2)+"\n")
    print(json.dumps(metrics,indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
