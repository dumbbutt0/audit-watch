#!/usr/bin/env python3
"""P114 — Fresh-candidate terminal-state distribution (research-only, UN-WIRED).

Runs the assisted workflow on the NEXT 3 mechanically-selected fresh top-ranked candidates (after P113) and measures
the distribution of TRUTHFUL terminal states. This is not about forcing confirmations — it measures what the full
assisted process does when repeatedly applied to uncertain candidates. A run dominated by NEEDS_CONTEXT /
HARNESS_UNAVAILABLE is NOT failure: it means the pipeline preserves precision and is naming the next bottleneck. The
only failure is unsafe promotion, cherry-picking, missing evidence, or status leakage.

Selection (mechanical): the global recommended ranking across all subjects, excluding confirmed controls + already-run
candidates (incl. P113 RamsesV3Pool.swap) + missing-source subjects; the next 3 highest; full skip log. No manual
choice. Each candidate is run via the P113 orchestrator (assisted_fresh_run.run) with an HONEST source-derived
rationale (no fabricated evidence); package/READY are reachable ONLY through execution-backed CONFIRMED_RUNTIME.

Usage:
    python scripts/assisted/terminal_distribution.py --self-test
    python scripts/assisted/terminal_distribution.py --run
"""
from __future__ import annotations

import argparse
import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "assisted"))
sys.path.insert(0, str(ROOT / "scripts" / "investigation"))
import assisted_fresh_run as AFR             # noqa: E402  (P113 orchestrator; read-only reuse)
import rank_candidates_prototype as RANK     # noqa: E402  (P107 ranking; read-only)
import harness_prep as HP                     # noqa: E402  (P111; read-only)

FLAGS = {
    "is_gate": False,
    "research_only": True,
    "review_only": True,
    "routes_in_production": False,
    "routed_manifest_ids": [],
}

ASSISTED = ROOT / "documentation" / "research" / "assisted_mode"
DEFAULT_CORPUS = ASSISTED / "p105" / "benchmark_corpus.json"
DEFAULT_OUT = ASSISTED / "p114_terminal_distribution"

# candidates already run in prior phases (fresh-discovery), excluded here
ALREADY_RUN = {("ramses-2024-10", "RamsesV3Pool", "swap")}   # P113
LEAK_TOKENS = ('"submitted": true', "APPROVED_TO_SUBMIT", "READY_FOR_HUMAN_REVIEW", "SUBMITTED")

# HONEST per-candidate analyst rationales (from reading each function's source; NO fabricated exploit evidence).
# Keyed by (subject, contract, function). Evidence is None for all -> truthful NEEDS_CONTEXT.
RATIONALES: Dict[Tuple[str, str, str], str] = {
    ("wildcat-2024-08", "WildcatMarket", "closeMarket"): (
        "Read WildcatMarket.closeMarket. It is `onlyBorrower nonReentrant sphereXGuardExternal` — a PRIVILEGED "
        "borrower-only function, NOT a permissionless attacker path. (Note: the recommended ranking marked it "
        "permissionless because the body-only actor_clarity heuristic misses the `onlyBorrower` MODIFIER, which is in "
        "the signature, not the body — a ranking-precision gap.) Its closed-market accounting feeds the state that "
        "the awarded P95 H-01 exploited, but that bug lives in the sibling permissionless `executeWithdrawal`, not "
        "here. I could not form a source-provable exploit on closeMarket (privileged caller) and could not prove it "
        "safe (complex closed-market settlement); resolving it needs the cross-function/runtime path. Truthful "
        "terminal: NEEDS_CONTEXT."),
    ("wildcat-2024-08", "WildcatMarketWithdrawals", "repayAndProcessUnpaidWithdrawalBatches"): (
        "Read WildcatMarketWithdrawals.repayAndProcessUnpaidWithdrawalBatches. It is `public nonReentrant "
        "sphereXGuardExternal`; calling it pulls the caller's assets in (safeTransferFrom) to repay debt and then "
        "processes unpaid batches with `satSub`-guarded available-liquidity accounting — i.e. calling it DONATES "
        "funds, not extracts them. Any real issue would be inside `_processUnpaidWithdrawalBatch`'s pro-rata math "
        "(the awarded executeWithdrawal class), which cannot be confirmed or refuted from source alone. No "
        "source-provable exploit; not provably safe. Truthful terminal: NEEDS_CONTEXT."),
    ("phi-2024-08", "PhiNFT1155", "claimFromFactory"): (
        "Read PhiNFT1155.claimFromFactory. It is `external payable whenNotPaused onlyPhiFactory` — gated to the "
        "PhiFactory contract, NOT permissionless. (Same ranking gap: the body-only actor_clarity heuristic missed "
        "the `onlyPhiFactory` MODIFIER in the signature.) The attacker-facing entrypoint is `PhiFactory.claim`; the "
        "reward flow (handleRewardsAndGetValueSent) is cross-contract via PhiRewards. I could not form a "
        "source-provable exploit on claimFromFactory in isolation, nor prove it safe. Truthful terminal: "
        "NEEDS_CONTEXT."),
}


@lru_cache(maxsize=1)
def _cfg() -> Dict[str, Any]:
    return {"n": 3, "already_run": sorted("::".join(k) for k in ALREADY_RUN)}


def select_next_n(corpus: Dict[str, Any], n: int = 3,
                  already_run: Optional[set] = None) -> Dict[str, Any]:
    """Deterministic: rank all public/external functions by the recommended feature set; exclude confirmed controls +
    already-run + missing-source; return the next `n` highest + a full skip log of every excluded candidate seen."""
    already_run = already_run if already_run is not None else set(ALREADY_RUN)
    surfaces = RANK._surfaces(corpus)
    rows: List[Dict[str, Any]] = []
    for sid, s in surfaces.items():
        if not s["surface"]:
            continue
        for r in RANK.rank_surface(s["surface"], AFR.REC_FEATS):
            rows.append({"subject": sid, "contract": r["contract"], "function": r["function"],
                         "score": round(r["score"], 4), "permissionless": r["permissionless"]})
    # P115: permissionless soft gate cross-subject (mirrors rank_surface) — privileged functions (now correctly
    # flagged by signature-modifier-aware actor_clarity) are demoted below permissionless candidates.
    rows.sort(key=lambda x: (0 if x["permissionless"] else 1, -x["score"], x["subject"],
                             f"{x['contract']}.{x['function']}"))

    selected: List[Dict[str, Any]] = []
    skipped: List[Dict[str, Any]] = []
    for x in rows:
        key = (x["subject"], x["contract"], x["function"])
        if key in AFR.CONFIRMED_CONTROLS:
            skipped.append({**x, "reason": "excluded: confirmed positive control"})
            continue
        if key in already_run:
            skipped.append({**x, "reason": "excluded: already-run in a prior phase"})
            continue
        selected.append(x)
        if len(selected) >= n:
            break
    return {"selected": selected, "skipped": skipped, "considered_ranking_top": rows[:15],
            "total_candidates_ranked": len(rows),
            "selection_rule": ("recommended-feature score across all subjects; exclude confirmed controls + "
                               "already-run + missing-source; next N highest; deterministic tie-break (score, "
                               "subject, name)")}


def _candidate_id(c: Dict[str, Any]) -> str:
    import re
    return re.sub(r"[^A-Za-z0-9_.-]", "_", f"{c['subject']}__{c['contract']}_{c['function']}")


def run_batch(corpus: Dict[str, Any], n: int = 3, already_run: Optional[set] = None,
              rationales: Optional[Dict] = None) -> Dict[str, Any]:
    # P116: additive params — `already_run` extends the excluded set (P113+P114+...); `rationales` overrides the
    # per-candidate honest rationale map. Defaults preserve the P114 behavior exactly.
    rat = rationales if rationales is not None else RATIONALES
    sel = select_next_n(corpus, n=n, already_run=already_run)
    per_candidate = []
    for c in sel["selected"]:
        key = (c["subject"], c["contract"], c["function"])
        rationale = rat.get(key, "No source-backed exploit hypothesis was produced for this candidate; "
                                 "source analysis is insufficient to confirm or refute. Truthful terminal: "
                                 "NEEDS_CONTEXT.")
        # HONEST: analyst_evidence=None (no fabrication) -> truthful terminal
        r = AFR.run(c, analyst_evidence=None, analyst_rationale=rationale)
        per_candidate.append({"candidate_id": _candidate_id(c), "candidate": c, "result": r})

    # distribution + metrics
    dist: Dict[str, int] = {}
    metrics = []
    for pc in per_candidate:
        r = pc["result"]
        t = r["terminal_state"]
        dist[t] = dist.get(t, 0) + 1
        metrics.append({
            "candidate_id": pc["candidate_id"],
            "candidate": f"{pc['candidate']['subject']}::{pc['candidate']['contract']}.{pc['candidate']['function']}",
            "score": pc["candidate"]["score"],
            "terminal_state": t,
            "harness_class": r["stages"]["C0_harness_prep"]["classification"],
            "validation_decision": r["stages"]["B_validation"]["decision"],
            "validation_advanced": r["stages"]["B_validation"]["decision"] == "VALIDATED_FOR_POC_HANDOFF",
            "runtime_attempted": r["stages"]["C_runtime"]["attempted"],
            "package_allowed": t == "CONFIRMED_RUNTIME",
            "safety": r["safety"],
        })

    safety_all = all(all(m["safety"].values()) for m in metrics)
    no_package = all(not m["package_allowed"] for m in metrics) or all(
        m["runtime_attempted"] for m in metrics if m["package_allowed"])
    terminals_ok = all(m["terminal_state"] in AFR.TERMINALS for m in metrics)
    return {
        **FLAGS, "schema": "p114_terminal_distribution_v1",
        "selection": sel, "per_candidate": per_candidate,
        "terminal_distribution": dist, "metrics": metrics,
        "safety_all_pass": safety_all, "all_terminals_in_allowed_set": terminals_ok,
        "no_unsafe_package": no_package,
        "overall_pass": bool(safety_all and terminals_ok and no_package and len(sel["selected"]) == n),
    }


# ---------------------------------------------------------------------------- writers

def write_bundle(batch: Dict[str, Any], out_dir: Path) -> Dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    sel = batch["selection"]
    (out_dir / "candidate_selection.md").write_text(_selection_md(sel), encoding="utf-8")
    (out_dir / "selection.json").write_text(json.dumps(sel, indent=2) + "\n", encoding="utf-8")

    pc_root = out_dir / "per_candidate"
    pc_root.mkdir(exist_ok=True)
    for pc in batch["per_candidate"]:
        d = pc_root / pc["candidate_id"]
        d.mkdir(parents=True, exist_ok=True)
        r = pc["result"]
        (d / "intake.json").write_text(json.dumps(r["stages"]["A_intake"], indent=2) + "\n", encoding="utf-8")
        (d / "validation_decision.json").write_text(
            json.dumps(r["stages"]["B_validation"], indent=2) + "\n", encoding="utf-8")
        HP.write_bundle(r["_prep"], out_dir=d / "harness_prep")
        (d / "minimal_reproduction.md").write_text(AFR._minimal_repro_md(r), encoding="utf-8")
        (d / "runtime_result.json").write_text(
            json.dumps({"terminal_state": r["terminal_state"], "runtime": r["stages"]["C_runtime"],
                        "safety": r["safety"], "overall_truthful": r["overall_truthful"]}, indent=2) + "\n",
            encoding="utf-8")

    (out_dir / "terminal_distribution.json").write_text(
        json.dumps({"terminal_distribution": batch["terminal_distribution"], "metrics": batch["metrics"],
                    "safety_all_pass": batch["safety_all_pass"],
                    "all_terminals_in_allowed_set": batch["all_terminals_in_allowed_set"],
                    "no_unsafe_package": batch["no_unsafe_package"], "overall_pass": batch["overall_pass"]},
                   indent=2) + "\n", encoding="utf-8")
    (out_dir / "terminal_distribution_report.md").write_text(_report_md(batch), encoding="utf-8")
    return {"dir": str(out_dir)}


def _selection_md(sel: Dict[str, Any]) -> str:
    L = ["# P114 — Candidate selection (mechanical, next 3)", "",
         f"**Rule:** {sel['selection_rule']}", "",
         f"Total functions ranked: {sel['total_candidates_ranked']}.", "",
         "## Selected (next 3 highest remaining)"]
    for i, c in enumerate(sel["selected"], 1):
        L.append(f"{i}. `{c['subject']} :: {c['contract']}.{c['function']}` (score {c['score']})")
    L += ["", "## Skipped (excluded by rule)"]
    if sel["skipped"]:
        for s in sel["skipped"]:
            L.append(f"- `{s['subject']}::{s['contract']}.{s['function']}` (score {s['score']}) — {s['reason']}")
    else:
        L.append("- none above the selected three")
    L += ["", "## Considered ranking (top 15, audit)", "",
          "| # | score | subject | contract.function |", "|---|---|---|---|"]
    for i, x in enumerate(sel["considered_ranking_top"], 1):
        L.append(f"| {i} | {x['score']} | {x['subject']} | {x['contract']}.{x['function']} |")
    L += ["", "_No manual cherry-picking; selection is the deterministic next-3 of the recommended ranking._", ""]
    return "\n".join(L) + "\n"


def _report_md(b: Dict[str, Any]) -> str:
    L = ["# P114 — Fresh-candidate terminal-state distribution", "",
         f"**OVERALL PASS: {b['overall_pass']}**  ·  research-only, un-wired. 3 mechanically-selected fresh "
         "candidates run to truthful terminal states.", "",
         "## Terminal distribution",
         f"- {json.dumps(b['terminal_distribution'])}", "",
         "## Per candidate",
         "| Candidate | score | terminal | harness | validation | runtime tried | package allowed |",
         "|---|---|---|---|---|---|---|"]
    for m in b["metrics"]:
        L.append(f"| {m['candidate']} | {m['score']} | {m['terminal_state']} | {m['harness_class']} | "
                 f"{m['validation_decision']} | {m['runtime_attempted']} | {m['package_allowed']} |")
    L += ["", "## Safety",
          f"- all safety assertions pass: {b['safety_all_pass']}",
          f"- all terminals in allowed set: {b['all_terminals_in_allowed_set']}",
          f"- no unsafe package (package only on CONFIRMED_RUNTIME): {b['no_unsafe_package']}", "",
          "## Honest interpretation",
          "- A distribution dominated by NEEDS_CONTEXT / HARNESS_UNAVAILABLE is NOT failure — it is the pipeline "
          "preserving precision and naming the next bottleneck.",
          "- Observed next bottleneck: the recommended ranking's body-only `actor_clarity` signal misses access "
          "MODIFIERS declared in the function signature (`onlyBorrower`, `onlyPhiFactory`), so privileged functions "
          "can rank as 'permissionless'. Honest validation caught this; a future ranking iteration should read "
          "signature modifiers. Ranking chose the order; it did not validate anything.", "",
          "## Per-candidate rationale"]
    for pc in b["per_candidate"]:
        L.append(f"- **{pc['candidate_id']}**: {pc['result']['analyst_rationale']}")
    L.append("")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------------------- self-test

def _self_test() -> int:
    ok = True

    def chk(cond, m):
        nonlocal ok
        ok &= bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {m}")

    chk(FLAGS["is_gate"] is False and FLAGS["routes_in_production"] is False, "FLAGS un-wired")
    if not DEFAULT_CORPUS.is_file():
        print("  [SKIP] corpus absent")
        print("SELF-TEST:", "OK" if ok else "FAILED")
        return 0 if ok else 1
    corpus = json.loads(DEFAULT_CORPUS.read_text(encoding="utf-8"))

    sel = select_next_n(corpus, n=3)
    keys = {(c["subject"], c["contract"], c["function"]) for c in sel["selected"]}
    chk(len(sel["selected"]) == 3, "exactly 3 selected")
    chk(("ramses-2024-10", "RamsesV3Pool", "swap") not in keys, "P113 candidate excluded")
    chk(not (keys & AFR.CONFIRMED_CONTROLS), "confirmed controls excluded")
    chk(any(s["reason"].startswith("excluded: already-run") for s in sel["skipped"]), "skip log records already-run")
    # P115: with signature-modifier-aware actor_clarity + the cross-subject permissionless gate, the privileged
    # functions closeMarket (onlyBorrower) and claimFromFactory (onlyPhiFactory) are DEMOTED out of the top.
    chk(("wildcat-2024-08", "WildcatMarket", "closeMarket") not in keys, "P115: privileged closeMarket demoted")
    chk(("phi-2024-08", "PhiNFT1155", "claimFromFactory") not in keys, "P115: privileged claimFromFactory demoted")
    chk(all(c["permissionless"] for c in sel["selected"]), "P115: all selected candidates are permissionless")
    # determinism
    chk(json.dumps(sel, sort_keys=True) == json.dumps(select_next_n(corpus, n=3), sort_keys=True), "selection deterministic")

    b = run_batch(corpus, n=3)
    chk(len(b["per_candidate"]) == 3, "3 candidates run")
    chk(all(m["terminal_state"] in AFR.TERMINALS for m in b["metrics"]), "all terminals in allowed set")
    chk(all(m["terminal_state"] == "NEEDS_CONTEXT" for m in b["metrics"]),
        "honest (no-evidence) run -> all NEEDS_CONTEXT")
    chk(b["safety_all_pass"] and b["no_unsafe_package"], "safety holds; no unsafe package")
    chk(all(not m["package_allowed"] for m in b["metrics"]), "no package allowed (no runtime confirmation)")
    chk(b["overall_pass"], "overall pass")
    blob = json.dumps(b["metrics"]) + json.dumps(b["terminal_distribution"])
    chk(not any(t in blob for t in ('"submitted": true', "APPROVED_TO_SUBMIT")), "no auto-submit tokens in metrics")
    # determinism of the batch (drop volatile _prep)
    def _strip(x):
        c = json.loads(json.dumps({k: v for k, v in x.items()
                                   if k in ("terminal_distribution", "metrics", "overall_pass")}))
        return c
    chk(_strip(b) == _strip(run_batch(corpus, n=3)), "batch deterministic")

    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--corpus")
    ap.add_argument("--out-dir")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    if args.run:
        corpus = json.loads(Path(args.corpus or DEFAULT_CORPUS).read_text(encoding="utf-8"))
        b = run_batch(corpus, n=3)
        out = write_bundle(b, Path(args.out_dir) if args.out_dir else DEFAULT_OUT)
        print(f"P114 terminal distribution — OVERALL PASS={b['overall_pass']}")
        print(f"  distribution: {b['terminal_distribution']}")
        for m in b["metrics"]:
            print(f"  {m['candidate']:<55} {m['terminal_state']:<16} harness={m['harness_class']} "
                  f"val={m['validation_decision']} pkg_allowed={m['package_allowed']}")
        print(f"  safety_all_pass={b['safety_all_pass']} no_unsafe_package={b['no_unsafe_package']}")
        print(f"  -> {out['dir']}")
        return 0 if b["overall_pass"] else 1
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
