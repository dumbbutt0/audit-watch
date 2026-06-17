#!/usr/bin/env python3
"""P265 — analysis-only aggregator (NOT a production module; lives under the P265 deliverable dir).

Reads the 13 frozen shadow-harness outputs and computes the deterministic operational metrics
(#1 candidates/audit, #6 concluded/reportable FP, #8 recall-delta-vs-narrow-baseline) plus structural
counts that feed the scored/operator metrics written by hand in the docs. Generates/conducts NOTHING:
it only reads the already-emitted advisory outputs. No answer keys, no severity, no routing.

Narrow baseline = top-5 by P260 rank (prioritizer_score 0..4). Recall-delta candidate = rank >=5 OR
rank is None (forced into the sweep by a recall-first clause beyond the narrow top-5).
"""
import json
import glob
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"

# Honest scored-status of each trial contest (see SETUP.md).
SCORED = {
    "benddao": "clean_public_anchor",            # P263 public findings, training-confound accepted
    "monetrix": "unscored_private_findings",      # P261 findings repo private
    "concrete": "unscored_private_findings",      # P256: report 404 + private findings repo
    "reserve": "scored_contaminated_leaked",      # P257: reveal-precheck leaked award titles
}
CONTESTS = ["loopfi", "basin", "bakerfi", "plaza", "concrete", "notional", "reserve",
            "astaria", "ethos", "hybra", "sentiment", "benddao", "monetrix"]
NARROW_TOPN = 5  # P260 narrow baseline depth


def scored_status(name):
    return SCORED.get(name, "scored_contaminated_retrospective")


def load(name):
    md = OUT / name / "recall_metrics.json"
    ad = OUT / name / "recall_advisory_candidates.json"
    gd = OUT / name / "recall_guard_report.json"
    return json.loads(md.read_text()), json.loads(ad.read_text()), json.loads(gd.read_text())


# Operator-triage proxy (metric #2/#7). TRANSPARENT RUBRIC, not a human study:
# a lead is "worth human review" if it is BOTH (a) recall-delta (forced beyond narrow top-5, so the old
# narrow path would have skipped it) AND (b) carries an award-class-fit template family (the families that
# actually carried awards across P254-263: T1 external-dep DoS, T2 redemption coupling, T5 liveness,
# T7 solvency, T8 share-price/inflation) AND (c) has a real checkpoint EVIDENCE-marker hit (not just a name).
WORTH_REVIEW_FAMILIES = ("T1_", "T2_", "T5_", "T7_", "T8_")
MIN_PER_CANDIDATE_TRIAGE = 4.0  # operator minutes to read mechanism hypotheses + falsification Qs per candidate


def _worth_review(c):
    is_delta = (c.get("prioritizer_score") is None) or (c.get("prioritizer_score") >= NARROW_TOPN)
    fam = any(t.startswith(f) for t in c.get("templates_applied", []) for f in WORTH_REVIEW_FAMILIES)
    ev = "checkpoint_hit_evidence_marker" in c.get("sweep_inclusion_reason", [])
    return is_delta and fam and ev


def per_contest(name):
    m, a, g = load(name)
    cands = a["advisory_candidates"]
    n = len(cands)
    narrow, delta = [], []
    for c in cands:
        r = c.get("prioritizer_score")
        if r is not None and r < NARROW_TOPN:
            narrow.append(c)
        else:
            delta.append(c)  # rank >=5 or None -> forced in beyond narrow baseline
    worth = [c for c in cands if _worth_review(c)]
    n_worth = len(worth)
    # minutes per useful lead = (all candidates triaged * min/candidate) / useful leads
    min_per_useful = round((n * MIN_PER_CANDIDATE_TRIAGE) / n_worth, 1) if n_worth else None
    return {
        "contest": name,
        "scored_status": scored_status(name),
        "advisory_candidates": n,                       # metric #1
        "guard_violations": m["guard_violations"],      # metric #6 (must be 0)
        "guard_result": g["result"],
        "checkpoint_hit_functions": m["checkpoint_hit_functions"],
        "total_manifest_functions": m["total_manifest_functions"],
        "narrow_baseline_count": len(narrow),
        "recall_delta_count": len(delta),               # metric #8 denominator-side
        "recall_delta_fraction": round(len(delta) / n, 3) if n else 0.0,
        "worth_review_count": n_worth,                   # metric #2 (proxy)
        "worth_review_fraction": round(n_worth / n, 3) if n else 0.0,
        "operator_minutes_per_useful_lead": min_per_useful,  # metric #7 (proxy)
        "templates_applied": m["templates_applied"],
        "mechanisms_generated": m["mechanisms_generated"],
        "mechanisms_truncated": m["mechanisms_truncated"],
        "forced_loci_by_clause": m["forced_loci_by_clause"],
        "runtime_seconds": m["runtime_seconds"],
        "version_hashes": m["version_hashes"],
    }


def main():
    rows = [per_contest(c) for c in CONTESTS]
    total_c = sum(r["advisory_candidates"] for r in rows)
    total_delta = sum(r["recall_delta_count"] for r in rows)
    total_narrow = sum(r["narrow_baseline_count"] for r in rows)
    total_viol = sum(r["guard_violations"] for r in rows)
    total_worth = sum(r["worth_review_count"] for r in rows)
    hashes = {r["contest"]: r["version_hashes"] for r in rows}
    # confirm every contest ran on the same frozen module/config set
    unique_hashes = {json.dumps(h, sort_keys=True) for h in hashes.values()}
    agg = {
        "module": "p265_aggregate (analysis-only, research)",
        "is_gate": False, "research_only": True, "routes_in_production": False,
        "emits_findings": False, "concludes_vulnerability": False,
        "trial_contests": len(rows),
        "pooled": {
            "advisory_candidates_total": total_c,                       # #1 pooled
            "advisory_candidates_per_audit_mean": round(total_c / len(rows), 2),
            "advisory_candidates_min": min(r["advisory_candidates"] for r in rows),
            "advisory_candidates_max": max(r["advisory_candidates"] for r in rows),
            "concluded_reportable_FP_total": total_viol,                # #6 pooled (must be 0)
            "guard_all_pass": all(r["guard_result"] == "PASS" for r in rows),
            "narrow_baseline_total": total_narrow,
            "recall_delta_total": total_delta,                         # #8 pooled
            "recall_delta_fraction_pooled": round(total_delta / total_c, 3),
            "worth_review_total": total_worth,                          # #2 pooled (proxy)
            "worth_review_fraction_pooled": round(total_worth / total_c, 3),
            "operator_minutes_per_useful_lead_pooled": round(
                (total_c * MIN_PER_CANDIDATE_TRIAGE) / total_worth, 1) if total_worth else None,  # #7 pooled (proxy)
        },
        "frozen_inputs_identical_across_runs": len(unique_hashes) == 1,
        "version_hashes_sample": rows[0]["version_hashes"],
        "per_contest": rows,
    }
    (OUT / "p265_aggregate_metrics.json").write_text(json.dumps(agg, indent=2))
    print(json.dumps(agg["pooled"], indent=2))
    print("frozen_inputs_identical_across_runs:", agg["frozen_inputs_identical_across_runs"])
    print("\ncontest      cand  delta  worth  min/lead  guard  scored-status")
    for r in rows:
        print(f"{r['contest']:11s}  {r['advisory_candidates']:4d}  {r['recall_delta_count']:5d}  "
              f"{r['worth_review_count']:5d}  {str(r['operator_minutes_per_useful_lead']):>7s}  "
              f"{r['guard_result']:5s}  {r['scored_status']}")


if __name__ == "__main__":
    main()
