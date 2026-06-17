#!/usr/bin/env python3
"""P107 — Evidence-free ranking prototype (research-only, UN-WIRED). "Ranker: prioritize, don't promote."

Orders the ALREADY-ENUMERATED public/external surface of each P105 subject using ONLY the P106-allowed evidence-free
signals, and measures whether that beats alphabetical ordering on top-k recall of the awarded function. It is an
experiment, not a pipeline stage: it adds no detector, calls NO validation, writes no funnel/PoC state, changes no
threshold, and marks nothing validated / poc-ready / report-ready / submission-ready.

Score features (equal-weight, per-subject-normalized): consequence_value_movement, consequence_fund_reachability,
exploitability_external_call, missing_update_asymmetry, state_write_breadth.
Gate-only (soft, two-tier sort — never a score boost): actor_clarity / permissionless_entry.
Excluded from pre-validation ranking (P106): defense_gap (negative lift), category_specificity (saturated).

Reuses the frozen P106 probe read-only (build_surface / _percentile / _resolve_sol_files); computes no new features.

Usage:
    python scripts/assisted/rank_candidates_prototype.py --self-test
    python scripts/assisted/rank_candidates_prototype.py --run    # -> p107/{ranking_results,ranking_report,ablation_report}
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "assisted"))

import rank_signal_probe as PROBE  # noqa: E402  (P106; read-only reuse — build_surface/_percentile/_resolve_sol_files)

FLAGS = {
    "is_gate": False,
    "research_only": True,
    "review_only": True,
    "routes_in_production": False,
    "routed_manifest_ids": [],
}

DEFAULT_CORPUS = ROOT / "documentation" / "research" / "assisted_mode" / "p105" / "benchmark_corpus.json"
DEFAULT_OUT = ROOT / "documentation" / "research" / "assisted_mode" / "p107"

# the only feature that is a count (needs per-subject percentile normalization); the rest are binary 0/1.
_NUMERIC = {"state_write_breadth"}
# gate-only signal — never enters a score.
_GATE = "actor_clarity"

SHARP = ["consequence_value_movement", "consequence_fund_reachability", "exploitability_external_call"]
MODERATE = ["missing_update_asymmetry", "state_write_breadth"]

VARIANTS: Dict[str, List[str]] = {
    "alphabetical_baseline": [],                                   # name sort only
    "sharp_only": list(SHARP),
    "sharp_plus_moderate": SHARP + MODERATE,
    "conservative": ["consequence_value_movement", "consequence_fund_reachability"],
    "no_external_call_ablation": ["consequence_value_movement", "consequence_fund_reachability",
                                  "missing_update_asymmetry", "state_write_breadth"],
}

TOPK = [1, 3, 5, 10]
PROMOTION_FORBIDDEN = ("validated", "poc_ready", "poc_lock", "report_ready", "submission_ready", "SUBMITTED",
                       "severity_assigned")


@lru_cache(maxsize=1)
def _cfg() -> Dict[str, Any]:
    return {"topk": list(TOPK), "noise_threshold": 3, "worst_case_tolerance": 0.10}


# ---------------------------------------------------------------------------- scoring

def _normalized_columns(surface: Dict[Tuple[str, str], Dict[str, Any]]) -> Dict[str, List[float]]:
    """Per-feature column of raw values across the subject surface (for percentile normalization of numerics)."""
    cols: Dict[str, List[float]] = {f: [] for f in PROBE.FEATURES}
    for rec in surface.values():
        for f in PROBE.FEATURES:
            cols[f].append(rec["features"][f])
    return cols


def _feature_norm(feat: str, value: float, col: List[float]) -> float:
    """Binary features contribute 0/1; numeric features contribute their within-subject percentile (0..1)."""
    if feat in _NUMERIC:
        return PROBE._percentile(col, value)
    return 1.0 if value > 0 else 0.0


def _score(rec: Dict[str, Any], feats: List[str], cols: Dict[str, List[float]]) -> float:
    if not feats:
        return 0.0
    return round(sum(_feature_norm(f, rec["features"][f], cols[f]) for f in feats), 6)


def _permissionless(rec: Dict[str, Any]) -> bool:
    return rec["features"].get(_GATE, 0.0) > 0


def rank_surface(surface: Dict[Tuple[str, str], Dict[str, Any]], feats: List[str]) -> List[Dict[str, Any]]:
    """Return the surface ordered by (permissionless soft-gate tier, -score, alphabetical name). Deterministic.
    The soft gate demotes role-guarded functions to tier 2; it never drops them (recall-preserving)."""
    cols = _normalized_columns(surface)
    rows = []
    for (contract, fn), rec in surface.items():
        rows.append({
            "contract": contract, "function": fn, "name": f"{contract}.{fn}",
            "score": _score(rec, feats, cols),
            "permissionless": _permissionless(rec),
        })
    # tier 0 = permissionless first; then higher score; then alphabetical (so baseline == pure name sort)
    rows.sort(key=lambda r: (0 if r["permissionless"] else 1, -r["score"], r["name"]))
    for i, r in enumerate(rows):
        r["rank"] = i + 1
    return rows


def _awarded_rank(ranked: List[Dict[str, Any]], contract: str, fn: str) -> Optional[Dict[str, Any]]:
    for r in ranked:
        if r["contract"] == contract and r["function"] == fn:
            return r
    return None


# ---------------------------------------------------------------------------- corpus run

def _surfaces(corpus: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Build each subject's feature surface once (reused across all variants)."""
    excludes = corpus.get("exclude_substrings", [])
    out = {}
    for spec in corpus.get("subjects", []):
        built = PROBE.build_surface(spec, excludes)
        out[spec["id"]] = {"spec": spec, "surface": built["surface"], "size": len(built["surface"])}
    return out


def _awarded_list(corpus: Dict[str, Any]) -> List[Tuple[str, Dict[str, Any]]]:
    out = []
    for spec in corpus.get("subjects", []):
        for f in spec.get("awarded_findings", []):
            if f.get("surfaceable"):
                out.append((spec["id"], f))
    return out


def evaluate_variant(surfaces: Dict[str, Dict[str, Any]], awarded: List[Tuple[str, Dict[str, Any]]],
                     feats: List[str]) -> Dict[str, Any]:
    ranked_by_subject = {sid: rank_surface(s["surface"], feats) for sid, s in surfaces.items()}
    rows = []
    for sid, finding in awarded:
        ranked = ranked_by_subject[sid]
        ar = _awarded_rank(ranked, finding["contract"], finding["function"])
        rows.append({
            "finding_id": finding["finding_id"], "subject": sid,
            "contract": finding["contract"], "function": finding["function"],
            "rank": ar["rank"] if ar else None,
            "score": ar["score"] if ar else None,
            "surface_size": surfaces[sid]["size"],
            "found": ar is not None,
        })
    return {"per_finding": rows, "metrics": _metrics(rows)}


def _metrics(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    ranks = [r["rank"] for r in rows if r["rank"] is not None]
    n = len(rows)
    m = {f"top_{k}_recall": round(sum(1 for r in ranks if r <= k) / n, 4) if n else None for k in TOPK}
    m.update({
        "n": n,
        "mean_rank": round(statistics.mean(ranks), 4) if ranks else None,
        "median_rank": round(statistics.median(ranks), 4) if ranks else None,
        "worst_rank": max(ranks) if ranks else None,
        # evidence-free-unrankable: scored 0 on this variant's features (buried in the alphabetical tie)
        "unrankable_count": sum(1 for r in rows if (r["score"] or 0) == 0),
        "unrankable_findings": [r["finding_id"] for r in rows if (r["score"] or 0) == 0],
    })
    return m


def _per_architecture(surfaces, awarded, feats) -> Dict[str, Any]:
    out = {}
    ranked_by_subject = {sid: rank_surface(s["surface"], feats) for sid, s in surfaces.items()}
    for sid, finding in awarded:
        ar = _awarded_rank(ranked_by_subject[sid], finding["contract"], finding["function"])
        out.setdefault(sid, []).append({"finding_id": finding["finding_id"],
                                        "rank": ar["rank"] if ar else None,
                                        "surface_size": surfaces[sid]["size"]})
    return out


# ---------------------------------------------------------------------------- ablation + hard stops

def run_ablation(surfaces, awarded) -> Dict[str, Any]:
    """From sharp_plus_moderate, drop each score feature once. A feature is eligible iff dropping it WORSENS top-k
    recall or mean rank, AND keeping it does not materially worsen worst-case rank vs dropping it."""
    full_feats = VARIANTS["sharp_plus_moderate"]
    full = evaluate_variant(surfaces, awarded, full_feats)["metrics"]
    tol = _cfg()["worst_case_tolerance"]
    results = {}
    for feat in full_feats:
        reduced = [f for f in full_feats if f != feat]
        red = evaluate_variant(surfaces, awarded, reduced)["metrics"]
        topk_worsened = any((full[f"top_{k}_recall"] or 0) > (red[f"top_{k}_recall"] or 0) for k in TOPK)
        mean_worsened = (red["mean_rank"] or 0) > (full["mean_rank"] or 0)
        # does INCLUDING feat materially worsen worst case? (full worst vs reduced worst, relative tolerance)
        worst_full, worst_red = full["worst_rank"] or 0, red["worst_rank"] or 0
        worst_inflated_by_feat = worst_full > worst_red * (1 + tol) and worst_full > worst_red
        eligible = bool((topk_worsened or mean_worsened) and not worst_inflated_by_feat)
        results[feat] = {
            "removal_top_k_delta": {f"top_{k}_recall": round((red[f"top_{k}_recall"] or 0)
                                                             - (full[f"top_{k}_recall"] or 0), 4) for k in TOPK},
            "removal_mean_rank_delta": round((red["mean_rank"] or 0) - (full["mean_rank"] or 0), 4),
            "removal_worsens_topk": topk_worsened,
            "removal_worsens_mean_rank": mean_worsened,
            "inclusion_worsens_worst_case": worst_inflated_by_feat,
            "eligible": eligible,
        }
    return {"baseline_full_metrics": full, "per_feature": results}


def _hard_stops(surfaces, awarded, variant_results, ablation) -> Dict[str, Any]:
    base = variant_results["alphabetical_baseline"]["metrics"]
    flags = {}

    # HS1 — cross-contract-only: do gains survive EXCLUDING iq-ai?
    non_iq = [(sid, f) for sid, f in awarded if sid != "iq-ai-2025-01"]
    hs1 = {}
    for vname, feats in VARIANTS.items():
        if vname == "alphabetical_baseline":
            continue
        full_m = variant_results[vname]["metrics"]
        ex_m = evaluate_variant(surfaces, non_iq, feats)["metrics"]
        base_ex = evaluate_variant(surfaces, non_iq, [])["metrics"]
        beats_full = (full_m["top_3_recall"] or 0) > (base["top_3_recall"] or 0)
        beats_ex = (ex_m["top_3_recall"] or 0) > (base_ex["top_3_recall"] or 0)
        hs1[vname] = {"beats_with_iqai": beats_full, "beats_without_iqai": beats_ex,
                      "only_helps_iqai": bool(beats_full and not beats_ex)}
    flags["HS1_cross_contract_only"] = {"per_variant": hs1,
                                        "tripped": any(v["only_helps_iqai"] for v in hs1.values())}

    # HS2 — noise-over-signal: per score feature, # subjects where >=nt non-awarded fns outrank the awarded fn
    # under that feature ALONE (sole-feature noisiness). A feature is GENUINELY net-harmful only if it is ALSO
    # ablation-ineligible; noisy-alone-but-ablation-eligible features are weak combined signals, not disqualifiers.
    nt = _cfg()["noise_threshold"]
    hs2 = {}
    for feat in SHARP + MODERATE:
        bad_subjects = 0
        for sid, finding in awarded:
            ranked = rank_surface(surfaces[sid]["surface"], [feat])
            ar = _awarded_rank(ranked, finding["contract"], finding["function"])
            if ar and (ar["score"] or 0) > 0 and (ar["rank"] - 1) >= nt:
                bad_subjects += 1   # >=nt functions strictly above the awarded fn under this single feature
        ablation_eligible = bool(ablation["per_feature"].get(feat, {}).get("eligible"))
        hs2[feat] = {"subjects_noise_outranks": bad_subjects,
                     "noisy_alone": bad_subjects >= 2,
                     "ablation_eligible": ablation_eligible,
                     "net_harmful": bool(bad_subjects >= 2 and not ablation_eligible)}
    net_harmful = [f for f, v in hs2.items() if v["net_harmful"]]
    flags["HS2_noise_over_signal"] = {
        "per_feature": hs2,
        "net_harmful_features": net_harmful,
        "sole_feature_noisy_features": [f for f, v in hs2.items() if v["noisy_alone"]],
        # literal (sole-feature) trip — transparent; resolved by dropping net-harmful features (the 'recommended' variant)
        "tripped_sole_feature": any(v["noisy_alone"] for v in hs2.values()),
        # the decision-relevant trip: a feature that is BOTH noisy-alone AND ablation-net-harmful remains in a variant
        "tripped": bool(net_harmful),
    }

    # HS3 — ablation fragility: every eligible-removed feature whose removal collapses topk gains is the signal;
    # tripped if NO feature is eligible (i.e. the gains do not depend on any feature -> not real)
    any_eligible = any(d["eligible"] for d in ablation["per_feature"].values())
    flags["HS3_ablation_fragility"] = {"any_feature_eligible": any_eligible, "tripped": not any_eligible}

    return flags


def _pass_fail(variant_results) -> Dict[str, Any]:
    base = variant_results["alphabetical_baseline"]["metrics"]
    winners = {}
    for vname, vr in variant_results.items():
        if vname == "alphabetical_baseline":
            continue
        m = vr["metrics"]
        beats = (
            (m["top_3_recall"] or 0) > (base["top_3_recall"] or 0)
            and (m["top_10_recall"] or 0) > (base["top_10_recall"] or 0)
            and (m["median_rank"] or 1e9) < (base["median_rank"] or 1e9)
        )
        winners[vname] = beats
    passing = [v for v, b in winners.items() if b]
    return {"baseline": base, "variant_beats_baseline": winners,
            "passing_variants": passing, "passed": bool(passing)}


# ---------------------------------------------------------------------------- driver

def run_corpus(corpus: Dict[str, Any]) -> Dict[str, Any]:
    surfaces = _surfaces(corpus)
    awarded = _awarded_list(corpus)
    variant_results = {
        v: {**evaluate_variant(surfaces, awarded, feats),
            "features": feats,
            "per_architecture": _per_architecture(surfaces, awarded, feats)}
        for v, feats in VARIANTS.items()
    }
    ablation = run_ablation(surfaces, awarded)
    # ablation-derived RECOMMENDED variant: SHARP features (the P106 discriminators) + only the MODERATE features
    # that pass the eligibility rule (drop net-harmful ones). This is the spec's "a feature stays eligible only
    # if..." rule applied to pick the final feature set.
    recommended_feats = list(SHARP) + [f for f in MODERATE if ablation["per_feature"].get(f, {}).get("eligible")]
    variant_results["recommended"] = {
        **evaluate_variant(surfaces, awarded, recommended_feats),
        "features": recommended_feats,
        "per_architecture": _per_architecture(surfaces, awarded, recommended_feats),
        "derivation": "SHARP + ablation-eligible MODERATE features (net-harmful features dropped)",
    }
    hard_stops = _hard_stops(surfaces, awarded, variant_results, ablation)
    verdict = _pass_fail(variant_results)

    # synthesis: the honest overall call. Primary criteria + HS1/HS3 + the recommended variant must exclude every
    # net-harmful feature (HS2 resolved by ablation-driven removal, not by ignoring it).
    net_harmful = hard_stops["HS2_noise_over_signal"]["net_harmful_features"]
    rec_feats = variant_results["recommended"]["features"]
    rec_excludes_harmful = all(f not in rec_feats for f in net_harmful)
    rec_beats = verdict["variant_beats_baseline"].get("recommended", False)
    synthesis = {
        "primary_criteria_met": verdict["passed"],
        "recommended_variant_features": rec_feats,
        "recommended_beats_baseline": rec_beats,
        "HS1_cross_contract_only_tripped": hard_stops["HS1_cross_contract_only"]["tripped"],
        "HS2_net_harmful_features": net_harmful,
        "HS2_recommended_excludes_net_harmful": rec_excludes_harmful,
        "HS3_ablation_fragility_tripped": hard_stops["HS3_ablation_fragility"]["tripped"],
        "overall_pass": bool(rec_beats and rec_excludes_harmful
                             and not hard_stops["HS1_cross_contract_only"]["tripped"]
                             and not hard_stops["HS3_ablation_fragility"]["tripped"]),
        "proceed_to_p108": None,  # set below
        "evidence_free_unrankable": sorted(set(
            variant_results["recommended"]["metrics"]["unrankable_findings"])),
        "demoted_by_ranking": [r["finding_id"] for r in variant_results["recommended"]["per_finding"]
                               if (a := next(x for x in variant_results["alphabetical_baseline"]["per_finding"]
                                             if x["finding_id"] == r["finding_id"]))
                               and r["rank"] is not None and a["rank"] is not None and r["rank"] > a["rank"]],
    }
    synthesis["proceed_to_p108"] = synthesis["overall_pass"]
    return {
        **FLAGS,
        "schema": "p107_ranking_results_v1",
        "invariant": "Ranker: prioritize, don't promote.",
        "note": ("Evidence-free ranking experiment over already-enumerated surfaces. NO validation, NO promotion, "
                 "NO PoC/report/submission locks, NO threshold change. Ranks are positions a human would scan; "
                 "ties broken alphabetically (baseline-comparable)."),
        "n_findings": len(awarded),
        "variants": variant_results,
        "ablation": ablation,
        "hard_stops": hard_stops,
        "verdict": verdict,
        "synthesis": synthesis,
    }


# ---------------------------------------------------------------------------- reports

def _fmt_pct(v):
    return f"{v:.0%}" if isinstance(v, (int, float)) else str(v)


def render_ranking_report(res: Dict[str, Any]) -> str:
    v = res["verdict"]
    s = res["synthesis"]
    L = ["# P107 — Evidence-free ranking prototype: results", "",
         f"**Invariant:** {res['invariant']}  ·  research-only, un-wired.  N findings = {res['n_findings']}.", "",
         "_Ranks are the position a human scanning the surface would reach the awarded function. Ties broken "
         "alphabetically so the baseline is exactly the P105/P106 status quo._", "",
         "## Synthesis (the honest call)",
         f"- **OVERALL PASS: {s['overall_pass']}** → proceed to P108: **{s['proceed_to_p108']}**",
         f"- Recommended variant = `{s['recommended_variant_features']}` "
         f"(SHARP + ablation-eligible moderates; net-harmful features dropped).",
         f"- Recommended beats baseline (top-3 ∧ top-10 ∧ median): **{s['recommended_beats_baseline']}**",
         f"- HS1 cross-contract-only tripped: {s['HS1_cross_contract_only_tripped']} · "
         f"HS3 ablation-fragility tripped: {s['HS3_ablation_fragility_tripped']}",
         f"- HS2 net-harmful features (noisy-alone AND ablation-ineligible): {s['HS2_net_harmful_features'] or 'none'}"
         f" — recommended excludes them: **{s['HS2_recommended_excludes_net_harmful']}**",
         f"- Findings the ranker DEMOTES vs alphabetical (the honest cost, ≈ P106 FM-4): {s['demoted_by_ranking']}",
         f"- Evidence-free-unrankable under recommended (scored 0): {s['evidence_free_unrankable']}", "",
         "## Verdict (primary criteria)",
         f"- **PASS: {v['passed']}** — a variant must beat alphabetical on top-3 recall AND top-10 recall AND "
         f"median rank.",
         f"- Passing variants: {v['passing_variants'] or 'none'}", "",
         "## Variant comparison",
         "| Variant | top-1 | top-3 | top-5 | top-10 | mean | median | worst | unrankable |",
         "|---|---|---|---|---|---|---|---|---|"]
    for vname, vr in res["variants"].items():
        m = vr["metrics"]
        L.append(f"| {vname} | {_fmt_pct(m['top_1_recall'])} | {_fmt_pct(m['top_3_recall'])} | "
                 f"{_fmt_pct(m['top_5_recall'])} | {_fmt_pct(m['top_10_recall'])} | {m['mean_rank']} | "
                 f"{m['median_rank']} | {m['worst_rank']} | {m['unrankable_count']} |")
    L += ["", "## Per-architecture (awarded rank by subject)", ""]
    # showcase the recommended (deliverable) variant if it passes, else the first passing, else sharp_plus_moderate
    show = ("recommended" if v["variant_beats_baseline"].get("recommended")
            else (v["passing_variants"][0] if v["passing_variants"] else "sharp_plus_moderate"))
    L.append(f"_Showing variant: **{show}** (vs alphabetical_baseline)._")
    L.append("| Subject | finding | rank (variant) | rank (alpha) | surface |")
    L.append("|---|---|---|---|---|")
    alpha = {r["finding_id"]: r for r in res["variants"]["alphabetical_baseline"]["per_finding"]}
    for r in res["variants"][show]["per_finding"]:
        a = alpha[r["finding_id"]]
        L.append(f"| {r['subject']} | {r['finding_id']} | {r['rank']} | {a['rank']} | {r['surface_size']} |")
    L += ["", "## Evidence-free-unrankable (scored 0 on the variant's features)",
          f"- {show}: {res['variants'][show]['metrics']['unrankable_findings']}",
          f"- sharp_plus_moderate: {res['variants']['sharp_plus_moderate']['metrics']['unrankable_findings']}", ""]
    L += ["## Hard-stop flags"]
    for name, fl in res["hard_stops"].items():
        L.append(f"- **{name}** — tripped: {fl['tripped']}")
    L += ["", "## Reading", "- A win on top-3/top-10/median means evidence-free signals move the awarded function "
          "up the human's scan order without any validation.", "- The unrankable set is the honest residual "
          "(P106 FM-4 access/index/cap/reward) — these need the validation layer (P108), not more ranking.", ""]
    return "\n".join(L) + "\n"


def render_ablation_report(res: Dict[str, Any]) -> str:
    ab = res["ablation"]
    L = ["# P107 — Ablation report", "",
         "From `sharp_plus_moderate`, each score feature is removed once. A feature is **eligible** iff its removal "
         "worsens top-k recall or mean rank, and including it does not materially worsen worst-case rank.", "",
         "## Full-variant baseline (sharp_plus_moderate)",
         f"- top-3 {_fmt_pct(ab['baseline_full_metrics']['top_3_recall'])} · "
         f"top-10 {_fmt_pct(ab['baseline_full_metrics']['top_10_recall'])} · "
         f"mean {ab['baseline_full_metrics']['mean_rank']} · median {ab['baseline_full_metrics']['median_rank']} · "
         f"worst {ab['baseline_full_metrics']['worst_rank']}", "",
         "## Per-feature (effect of REMOVING the feature)",
         "| Feature | Δtop-3 | Δtop-10 | Δmean rank | worsens top-k? | worsens mean? | inflates worst? | eligible |",
         "|---|---|---|---|---|---|---|---|"]
    for feat, d in ab["per_feature"].items():
        L.append(f"| {feat} | {d['removal_top_k_delta']['top_3_recall']} | "
                 f"{d['removal_top_k_delta']['top_10_recall']} | {d['removal_mean_rank_delta']} | "
                 f"{d['removal_worsens_topk']} | {d['removal_worsens_mean_rank']} | "
                 f"{d['inclusion_worsens_worst_case']} | **{d['eligible']}** |")
    keep = [f for f, d in ab["per_feature"].items() if d["eligible"]]
    drop = [f for f, d in ab["per_feature"].items() if not d["eligible"]]
    L += ["", f"**Eligible (earn their place):** {keep or 'none'}",
          f"**Not eligible (candidates to drop):** {drop or 'none'}",
          "", "_Δ are (reduced − full): negative Δrecall means removing the feature HURT recall (so the feature "
          "helps); positive Δmean rank means removal pushed the awarded function DOWN (feature helps)._", ""]
    return "\n".join(L) + "\n"


def write_outputs(res: Dict[str, Any], out_dir: Path) -> Dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    rj = out_dir / "ranking_results.json"
    rr = out_dir / "ranking_report.md"
    ar = out_dir / "ablation_report.md"
    rj.write_text(json.dumps(res, indent=2) + "\n", encoding="utf-8")
    rr.write_text(render_ranking_report(res), encoding="utf-8")
    ar.write_text(render_ablation_report(res), encoding="utf-8")
    return {"results": str(rj), "ranking_report": str(rr), "ablation_report": str(ar)}


def assert_no_promotion(res: Dict[str, Any]) -> bool:
    blob = json.dumps(res)
    return not any(tok in blob for tok in PROMOTION_FORBIDDEN)


# ---------------------------------------------------------------------------- self-test

_FIXTURE = (
    "// SPDX-License-Identifier: MIT\npragma solidity ^0.8.0;\n"
    "contract C {\n"
    "  mapping(address=>uint256) public bal; uint256 public total; address owner;\n"
    "  // awarded: permissionless, moves value, fund-reachable -> should rank HIGH\n"
    "  function withdrawAll() external { bal[msg.sender]+=1; total+=1; IERC20(t).transfer(msg.sender, total); }\n"
    "  // noise: alphabetically BEFORE 'withdrawAll' but no sharp signal -> baseline ranks it above; variant must not\n"
    "  function aaaPureView() external view returns (uint256) { return total; }\n"
    "  function bbbNoop() external view returns (uint256) { return total; }\n"
    "  // role-guarded admin fn -> soft gate demotes to tier 2 but does NOT drop\n"
    "  function setOwner(address o) external { require(msg.sender==owner); owner=o; }\n"
    "}\n"
)


def _self_test() -> int:
    ok = True

    def chk(cond, m):
        nonlocal ok
        ok &= bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {m}")

    chk(FLAGS["is_gate"] is False and FLAGS["routes_in_production"] is False, "FLAGS un-wired")

    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="p107_selftest_"))
    (tmp / "C.sol").write_text(_FIXTURE, encoding="utf-8")
    corpus = {
        "exclude_substrings": [],
        "subjects": [{
            "id": "fx", "phase": "self-test", "source_roots": [str(tmp)],
            "awarded_findings": [
                {"finding_id": "AWD", "contract": "C", "function": "withdrawAll",
                 "invariant_category": "per_user_accounting", "severity": "High",
                 "surfaceable": True, "grounding": "high"},
            ],
        }],
    }
    res = run_corpus(corpus)
    res2 = run_corpus(corpus)  # determinism + later surface reuse BEFORE fixture teardown

    base = res["variants"]["alphabetical_baseline"]["per_finding"][0]
    sharp = res["variants"]["sharp_plus_moderate"]["per_finding"][0]
    chk(base["found"] and sharp["found"], "awarded fn located in both variants")
    chk(base["rank"] >= 3, "baseline buries the awarded fn behind alphabetical noise (rank>=3)")
    chk(sharp["rank"] < base["rank"], "sharp variant ranks the awarded fn ABOVE alphabetical")
    chk(sharp["rank"] == 1, "value+fund-moving permissionless fn ranks #1 in the variant")

    # soft gate: role-guarded fn must still be present in the ranking (not dropped)
    ranked = rank_surface(_surfaces(corpus)["fx"]["surface"], VARIANTS["sharp_plus_moderate"])
    names = {r["function"] for r in ranked}
    chk("setOwner" in names, "soft gate keeps the role-guarded fn in the ranked set (tier 2, not dropped)")
    setowner = next(r for r in ranked if r["function"] == "setOwner")
    chk(setowner["permissionless"] is False, "role-guarded fn flagged non-permissionless (demoted tier)")

    # scoring/normalization
    cols = _normalized_columns(_surfaces(corpus)["fx"]["surface"])
    chk(_feature_norm("consequence_value_movement", 1.0, cols["consequence_value_movement"]) == 1.0,
        "binary feature normalizes to 1.0 when present")
    chk(0.0 <= _feature_norm("state_write_breadth", 5.0, [0, 1, 5]) <= 1.0, "numeric feature -> percentile in [0,1]")

    # determinism + no promotion
    chk(json.dumps(res, sort_keys=True) == json.dumps(res2, sort_keys=True), "deterministic on re-run")
    chk(assert_no_promotion(res), "output contains NO promotion/validation/poc/report/submission marker")
    chk("ablation" in res and "per_feature" in res["ablation"], "ablation computed")
    chk("verdict" in res and "passed" in res["verdict"], "verdict computed")

    for p in tmp.glob("*"):
        p.unlink()
    tmp.rmdir()

    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--corpus", help="path to benchmark_corpus.json (default: p105/benchmark_corpus.json)")
    ap.add_argument("--out-dir", help="default: documentation/research/assisted_mode/p107")
    args = ap.parse_args()

    if args.self_test:
        return _self_test()
    if args.run:
        corpus = json.loads(Path(args.corpus or DEFAULT_CORPUS).read_text(encoding="utf-8"))
        res = run_corpus(corpus)
        if not assert_no_promotion(res):
            print("ABORT: promotion marker found in output (HS5).", file=sys.stderr)
            return 2
        out = write_outputs(res, Path(args.out_dir) if args.out_dir else DEFAULT_OUT)
        v = res["verdict"]
        s = res["synthesis"]
        base = res["variants"]["alphabetical_baseline"]["metrics"]
        print(f"P107 — OVERALL PASS={s['overall_pass']}  proceed_to_p108={s['proceed_to_p108']}")
        print(f"  recommended features = {s['recommended_variant_features']}")
        print(f"  primary PASS={v['passed']}  passing={v['passing_variants']}")
        print(f"  HS2 net-harmful (dropped)={s['HS2_net_harmful_features']}  demoted-by-rank={s['demoted_by_ranking']}")
        print(f"  baseline: top3={base['top_3_recall']} top10={base['top_10_recall']} median={base['median_rank']}")
        for vn in VARIANTS:
            if vn == "alphabetical_baseline":
                continue
            m = res["variants"][vn]["metrics"]
            print(f"  {vn:28} top3={m['top_3_recall']} top10={m['top_10_recall']} "
                  f"median={m['median_rank']} mean={m['mean_rank']} worst={m['worst_rank']}")
        hs = {k: fl["tripped"] for k, fl in res["hard_stops"].items()}
        print(f"  hard_stops tripped: {hs}")
        print(f"  -> {out['results']}\n  -> {out['ranking_report']}\n  -> {out['ablation_report']}")
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
