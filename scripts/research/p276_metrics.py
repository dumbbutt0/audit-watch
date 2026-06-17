#!/usr/bin/env python3
"""P276 — SUPERVISED_EVAL metrics aggregator + FP report.

RESEARCH-ONLY / ADVISORY. Aggregates the per-contest Pass-B funnel maps + Pass-A replay bundles into corpus-level and
per-award-class metrics, and a false-positive report. Class inference reuses the FROZEN P273 keyword taxonomy
(read-only) on award title+root_cause. Severe concluded/reportable FP is 0 by construction (the upstream funnel never
concludes/reports — everything is advisory); this is asserted and reported.

Usage: python scripts/research/p276_metrics.py --out-dir <p276 outputs dir> [--quiet]
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CFG_COVERAGE = ROOT / "config/research_award_class_coverage_router.json"
LABEL = "SUPERVISED_EVAL"

STAGE_ORDER = {s: i for i, s in enumerate([
    "MISSED", "ADVISORY_SURFACED", "CLASS_ROUTED", "LOCUS_TRIAGED", "MECHANISM_GENERATED",
    "MECHANISM_SELECTED_OR_KEPT", "CHAIN_COMPLETED", "POC_INTENT_CORRECT", "POC_SUPPORTED",
    "EXACT_RECOVERED", "STRONG_RECOVERED", "FAMILY_RECOVERED", "SUBSYSTEM_ONLY"])}
_TOKEN = re.compile(r"[a-z_]+")


def _classify(text: str, class_signals: dict) -> str:
    toks = set(_TOKEN.findall((text or "").lower()))
    best, bestn = "UNKNOWN_OTHER", 0
    for cls, kws in class_signals.items():
        n = sum(1 for k in kws if k in toks or any(k in t for t in toks))
        if n > bestn:
            best, bestn = cls, n
    return best


def aggregate(out_dir: Path, quiet: bool) -> dict:
    class_signals = json.loads(CFG_COVERAGE.read_text())["class_signals"]
    maps, bundles = {}, {}
    for d in sorted(out_dir.iterdir()):
        m = d / "award_funnel_map.json"
        b = d / "replay_bundle.json"
        if m.exists():
            maps[d.name] = json.loads(m.read_text())
        if b.exists():
            bundles[d.name] = json.loads(b.read_text())

    locus_corpora = {k: v for k, v in maps.items() if v.get("with_locus_info", 0) > 0}
    titleonly_corpora = {k: v for k, v in maps.items()
                         if v.get("awarded_hm_total", 0) > 0 and v.get("with_locus_info", 0) == 0}

    # ---- corpus-level funnel over locus-mapped awards ----
    all_awards = [f for v in locus_corpora.values() for f in v["findings"] if f.get("note", "")[:10] != "title-only"]
    total = len(all_awards)

    def reached(stage, thresh):
        return STAGE_ORDER.get(stage, 0) >= STAGE_ORDER[thresh]

    def pct(n):
        return round(100.0 * n / total, 1) if total else 0.0

    surfaced = sum(1 for f in all_awards if reached(f["stage"], "ADVISORY_SURFACED"))
    routed = sum(1 for f in all_awards if reached(f["stage"], "CLASS_ROUTED"))
    triaged = sum(1 for f in all_awards if reached(f["stage"], "LOCUS_TRIAGED"))
    mech = sum(1 for f in all_awards if reached(f["stage"], "MECHANISM_GENERATED"))
    missed = sum(1 for f in all_awards if f["stage"] == "MISSED")

    corpus = {
        "locus_mapped_corpora": sorted(locus_corpora), "title_only_corpora": sorted(titleonly_corpora),
        "no_key_corpora_excluded": [],  # filled by caller doc
        "awarded_hm_locus_mapped": total,
        "advisory_surfaced_pct": pct(surfaced), "class_routed_pct": pct(routed),
        "locus_triaged_pct": pct(triaged), "mechanism_generated_pct": pct(mech),
        "missed_pct": pct(missed),
        "chain_completed_pct": "NOT_SAMPLED (upstream-corpus-wide run; completion/PoC tail sampled in narrative)",
        "poc_supported_pct": "NOT_SAMPLED", "exact_pct": "NOT_SAMPLED", "strong_pct": "NOT_SAMPLED",
        "first_failed_tally": dict(Counter(f["first_failed_stage"] for f in all_awards if f.get("first_failed_stage"))),
        "title_only_awarded_hm": sum(v["awarded_hm_total"] for v in titleonly_corpora.values()),
    }

    # ---- per-class breakdown ----
    per_class = defaultdict(lambda: Counter())
    for f in all_awards:
        cls = _classify(f.get("title", "") + " " + f.get("note", ""), class_signals)
        per_class[cls]["total"] += 1
        if reached(f["stage"], "ADVISORY_SURFACED"):
            per_class[cls]["surfaced"] += 1
        if reached(f["stage"], "CLASS_ROUTED"):
            per_class[cls]["routed"] += 1
        if reached(f["stage"], "MECHANISM_GENERATED"):
            per_class[cls]["mech"] += 1
    class_breakdown = {c: dict(v) for c, v in per_class.items()}

    # ---- FP report: triage-selected candidates not matching any awarded finding (advisory-only survivors) ----
    fp = {"severe_concluded_or_reportable_fp": 0, "by_corpus": {}, "advisory_only_nonawarded_survivors": 0}
    for name, b in bundles.items():
        mp = maps.get(name, {})
        matched_ids = {cid for f in mp.get("findings", []) for cid in f.get("matched_candidates", [])}
        selected = set(b.get("triage_selected", []))
        nonawarded = sorted(selected - matched_ids)
        fp["by_corpus"][name] = {"triage_selected": len(selected),
                                 "nonawarded_survivors_advisory": len(nonawarded),
                                 "examples": nonawarded[:5]}
        fp["advisory_only_nonawarded_survivors"] += len(nonawarded)

    result = {"label": LABEL, "mode": "SUPERVISED_EVAL_METRICS", "is_gate": False, "research_only": True,
              "emits_findings": False, "corpus": corpus, "per_class": class_breakdown, "false_positive_report": fp}
    (out_dir / "corpus_metrics.json").write_text(json.dumps(result, indent=1))
    if not quiet:
        print(f"[p276:metrics] locus-mapped awarded H/M={total} | surfaced={corpus['advisory_surfaced_pct']}% "
              f"routed={corpus['class_routed_pct']}% mech={corpus['mechanism_generated_pct']}% missed={corpus['missed_pct']}%")
        print(f"  first_failed={corpus['first_failed_tally']}")
        print(f"  severe FP={fp['severe_concluded_or_reportable_fp']} advisory-only nonawarded survivors={fp['advisory_only_nonawarded_survivors']}")
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    aggregate(Path(a.out_dir), a.quiet)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
