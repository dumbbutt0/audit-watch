#!/usr/bin/env python3
"""P113 — Fresh top-ranked assisted discovery run (research-only, UN-WIRED).

The first REAL assisted run on a fresh, not-confirmed candidate selected MECHANICALLY from the P107 recommended
ranking. The goal is NOT to force a finding — it is to move a fresh ranked candidate to a TRUTHFUL terminal state
without unsafe promotion or cherry-picking. A killed/inconclusive candidate is a PASS if the process is truthful; the
only failure is unsafe promotion, missing evidence, or manual cherry-picking. "Ranking only chooses investigation
order."

Selection rule: score every public/external function across all corpus subjects with the recommended feature set,
exclude confirmed positive controls / already-confirmed / missing-source-root subjects, pick the global highest
score (deterministic tie-break), record the skip log. No manual choice anywhere.

Allowed terminal states: CONFIRMED_RUNTIME, KILLED_RUNTIME, HARNESS_UNAVAILABLE, NEEDS_CONTEXT (and
READY_FOR_HUMAN_REVIEW only with execution-backed runtime evidence + pending human gate). Hard boundaries: no
auto-submit, no severity inflation, no package without runtime confirmation, no candidate advances for being ranked.

Reuses stage components read-only: rank_candidates_prototype, validate_candidate_invariant, harness_prep, funnel.

Usage:
    python scripts/assisted/assisted_fresh_run.py --self-test
    python scripts/assisted/assisted_fresh_run.py --run
"""
from __future__ import annotations

import argparse
import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "assisted"))
sys.path.insert(0, str(ROOT / "scripts" / "investigation"))
import rank_candidates_prototype as RANK    # noqa: E402  (P107; read-only — rank_surface)
import validate_candidate_invariant as V    # noqa: E402  (B validation; read-only)
import harness_prep as HP                    # noqa: E402  (C.0 harness prep, P111; read-only)

FLAGS = {
    "is_gate": False,
    "research_only": True,
    "review_only": True,
    "routes_in_production": False,
    "routed_manifest_ids": [],
}

ASSISTED = ROOT / "documentation" / "research" / "assisted_mode"
DEFAULT_CORPUS = ASSISTED / "p105" / "benchmark_corpus.json"
DEFAULT_OUT = ASSISTED / "p113_fresh_run"

# the P107 recommended feature set (SHARP + ablation-eligible moderate)
REC_FEATS = ["consequence_value_movement", "consequence_fund_reachability",
             "exploitability_external_call", "state_write_breadth"]
# confirmed positive controls (already reproduced) — excluded from a FRESH discovery run
CONFIRMED_CONTROLS = {("iq-ai-2025-01", "LiquidityManager", "moveLiquidity"),
                      ("secondswap-2024-12", "SecondSwap_Marketplace", "spotPurchase")}

CONFIRMED_RUNTIME, KILLED_RUNTIME, HARNESS_UNAVAILABLE, NEEDS_CONTEXT = (
    "CONFIRMED_RUNTIME", "KILLED_RUNTIME", "HARNESS_UNAVAILABLE", "NEEDS_CONTEXT")
TERMINALS = {CONFIRMED_RUNTIME, KILLED_RUNTIME, HARNESS_UNAVAILABLE, NEEDS_CONTEXT, "READY_FOR_HUMAN_REVIEW"}
LEAK_TOKENS = ('"submitted": true', "APPROVED_TO_SUBMIT", '"submission_status": "SUBMITTED"')


@lru_cache(maxsize=1)
def _cfg() -> Dict[str, Any]:
    return {"recommended_features": list(REC_FEATS)}


# ---------------------------------------------------------------------------- mechanical selection

def select_candidate(corpus: Dict[str, Any]) -> Dict[str, Any]:
    """Deterministic: global highest recommended-score public/external function, excluding confirmed controls /
    missing-source-root subjects. Returns the candidate + a transparent ranking + skip log."""
    surfaces = RANK._surfaces(corpus)
    rows: List[Dict[str, Any]] = []
    for sid, s in surfaces.items():
        if not s["surface"]:
            continue  # missing/empty source root -> excluded
        for r in RANK.rank_surface(s["surface"], REC_FEATS):
            rows.append({"subject": sid, "contract": r["contract"], "function": r["function"],
                         "score": round(r["score"], 4), "permissionless": r["permissionless"]})
    # P115: apply the permissionless SOFT GATE cross-subject (mirrors rank_surface) so privileged functions —
    # now correctly flagged via signature-modifier-aware actor_clarity — are demoted below permissionless ones.
    rows.sort(key=lambda x: (0 if x["permissionless"] else 1, -x["score"], x["subject"],
                             f"{x['contract']}.{x['function']}"))

    skipped: List[Dict[str, Any]] = []
    chosen: Optional[Dict[str, Any]] = None
    for x in rows:
        key = (x["subject"], x["contract"], x["function"])
        if key in CONFIRMED_CONTROLS:
            skipped.append({**x, "reason": "excluded: confirmed positive control / already-confirmed"})
            continue
        chosen = x
        break
    return {"candidate": chosen, "skipped_before_selection": skipped,
            "considered_ranking_top": rows[:12], "total_candidates_ranked": len(rows),
            "selection_rule": ("recommended-feature score across all subjects; exclude confirmed controls / "
                               "missing-source; highest remaining; deterministic tie-break (score, subject, name)")}


# ---------------------------------------------------------------------------- the run

def run(candidate: Dict[str, Any], analyst_evidence: Optional[Dict[str, Any]] = None,
        analyst_rationale: str = "", runtime_runner=None,
        corpus_path: Optional[str] = None) -> Dict[str, Any]:
    """Drive intake -> validation -> harness-prep -> truthful terminal. analyst_evidence is the HONEST source-derived
    {depth_trace, adversarial_ordering, impact_assessment} or None (no fabrication). runtime_runner, if provided,
    is the only way a CONFIRMED/KILLED runtime terminal can be reached."""
    subject, contract, function = candidate["subject"], candidate["contract"], candidate["function"]

    # A. intake
    intake = {
        **FLAGS, "subject": subject, "contract": contract, "function": function, "entrypoint": function,
        "candidate_invariant": (f"{contract}.{function} preserves its intended accounting/value-conservation "
                                "invariant; no permissionless actor can extract value beyond protocol fees"),
        "supplied_by": "p113_fresh_run (mechanical top-ranked selection)",
        "requested_check": "POC_HANDOFF",
        "source_refs": [f"{contract}.sol:{function}"],
    }

    # B. validation — uses ONLY honestly-supplied evidence (None -> NEEDS_MORE_CONTEXT, reject-first)
    vintake = {**intake}
    if analyst_evidence:
        vintake.update(analyst_evidence)
    vres = V.validate(vintake)
    validation = {"decision": vres.decision, "reason": vres.reason,
                  "analyst_evidence_supplied": bool(analyst_evidence)}

    # C.0 harness prep (always informative — effort estimate, never a gate)
    prep = HP.prepare(subject, contract, function, corpus_path=corpus_path)

    # C/C.0 -> terminal mapping
    runtime = {"attempted": False, "state": "NOT_ATTEMPTED", "reason": "", "evidence": None}
    if vres.decision == V.VALIDATED:
        # a validated hypothesis would go to runtime — but only a real runner can confirm/kill it
        if runtime_runner is not None:
            rr = runtime_runner(candidate, prep)
            runtime = {"attempted": True, **rr}
            terminal = CONFIRMED_RUNTIME if rr.get("confirmed") else (
                KILLED_RUNTIME if rr.get("killed") else HARNESS_UNAVAILABLE)
        else:
            runtime = {"attempted": False, "state": "HARNESS_UNAVAILABLE",
                       "reason": "no per-candidate exploit harness for a fresh candidate; building one is out of "
                                 "scope and unjustified without runtime evidence", "evidence": None}
            terminal = HARNESS_UNAVAILABLE
    elif vres.decision in (V.NEEDS_EXECUTION,):
        runtime = {"attempted": False, "state": "HARNESS_UNAVAILABLE",
                   "reason": "validation reached NEEDS_EXECUTION; no runnable per-candidate harness", "evidence": None}
        terminal = HARNESS_UNAVAILABLE
    else:
        # NEEDS_MORE_CONTEXT / NEEDS_CONTEXT / REJECTED_SOURCE_PROVEN_SAFE / BLOCKED_* -> no source-provable
        # hypothesis to run. Truthful terminal = NEEDS_CONTEXT (source analysis insufficient / not a runtime claim).
        terminal = NEEDS_CONTEXT

    # ---- safety enforcement (asserted) ----
    runtime_confirmed = (terminal == CONFIRMED_RUNTIME)
    package_emitted = runtime_confirmed                      # package ONLY on runtime confirmation
    ready_for_human_review = runtime_confirmed               # READY only with execution-backed evidence
    submitted = False                                        # never auto-submit
    severity_assigned = None                                 # never set severity

    assert terminal in TERMINALS, f"illegal terminal {terminal}"
    assert (not package_emitted) or runtime_confirmed, "submission package without runtime confirmation"
    assert (not ready_for_human_review) or runtime_confirmed, "READY without execution-backed evidence"

    result = {
        **FLAGS, "schema": "p113_fresh_run_v1",
        "candidate": candidate,
        "terminal_state": terminal,
        "stages": {
            "A_intake": intake,
            "B_validation": validation,
            "C0_harness_prep": {"classification": prep["harness_classification"],
                                "scaffold_inert": prep["scaffold_inert"],
                                "required_components": prep["required_components"]},
            "C_runtime": runtime,
        },
        "analyst_rationale": analyst_rationale,
        "safety": {
            "no_auto_submit": (submitted is False),
            "no_severity_inflation": (severity_assigned is None),
            "no_package_without_runtime": (package_emitted == runtime_confirmed),
            "no_ready_without_runtime": (ready_for_human_review == runtime_confirmed),
            "advanced_only_on_evidence_not_rank": (terminal != CONFIRMED_RUNTIME) or runtime["attempted"],
        },
        "_prep": prep,
    }
    result["overall_truthful"] = bool(terminal in TERMINALS and all(result["safety"].values()))
    return result


# ---------------------------------------------------------------------------- bundle writers

def _selection_md(sel: Dict[str, Any]) -> str:
    c = sel["candidate"]
    L = ["# P113 — Candidate selection (mechanical)", "",
         f"**Rule:** {sel['selection_rule']}", "",
         f"**Selected:** `{c['subject']} :: {c['contract']}.{c['function']}` "
         f"(recommended score {c['score']}, permissionless={c['permissionless']}).",
         f"Total functions ranked: {sel['total_candidates_ranked']}.", "",
         "## Skipped before selection (excluded by rule)"]
    if sel["skipped_before_selection"]:
        for s in sel["skipped_before_selection"]:
            L.append(f"- `{s['subject']}::{s['contract']}.{s['function']}` (score {s['score']}) — {s['reason']}")
    else:
        L.append("- none (the selected candidate is the global #1; no excluded candidate ranked above it)")
    L += ["", "## Considered ranking (top 12, for audit)", "",
          "| # | score | subject | contract.function | excluded? |", "|---|---|---|---|---|"]
    for i, x in enumerate(sel["considered_ranking_top"], 1):
        key = (x["subject"], x["contract"], x["function"])
        ex = "confirmed control" if key in CONFIRMED_CONTROLS else ""
        L.append(f"| {i} | {x['score']} | {x['subject']} | {x['contract']}.{x['function']} | {ex} |")
    L += ["", "_No manual cherry-picking: the candidate is the deterministic global maximum of the recommended "
          "ranking after excluding confirmed controls. Ranking only chooses investigation order._", ""]
    return "\n".join(L) + "\n"


def _report_md(r: Dict[str, Any]) -> str:
    c, s = r["candidate"], r["stages"]
    L = ["# P113 — Fresh discovery run: report", "",
         f"**Candidate:** `{c['subject']} :: {c['contract']}.{c['function']}` (recommended #1).",
         f"**Terminal state: {r['terminal_state']}**  ·  research-only, un-wired.", "",
         "## Stage path",
         f"- A intake — invariant supplied (mechanically selected candidate)",
         f"- B validation — `{s['B_validation']['decision']}` (analyst evidence supplied: "
         f"{s['B_validation']['analyst_evidence_supplied']})",
         f"  - reason: {s['B_validation']['reason']}",
         f"- C.0 harness prep — `{s['C0_harness_prep']['classification']}` (scaffold inert: "
         f"{s['C0_harness_prep']['scaffold_inert']})",
         f"- C runtime — attempted: {s['C_runtime']['attempted']}; state: {s['C_runtime']['state']}",
         f"  - {s['C_runtime'].get('reason','')}", "",
         "## Analyst rationale (honest source reading)", "", r["analyst_rationale"], "",
         "## Safety boundaries"]
    for k, v in r["safety"].items():
        L.append(f"- {k}: {v}")
    L += ["", f"**Overall truthful: {r['overall_truthful']}** — terminal in the allowed set, no safety boundary "
          "violated. No submission package, no human-review-ready state, no auto-submit, no severity assigned.",
          "", "_The #1 evidence-free-ranked function was investigated and honestly NOT promoted to a finding — "
          "ranking chose the order, not the verdict._", ""]
    return "\n".join(L) + "\n"


def _minimal_repro_md(r: Dict[str, Any]) -> str:
    c = r["candidate"]
    return ("# Minimal reproduction hypothesis\n\n"
            f"Candidate: `{c['subject']} :: {c['contract']}.{c['function']}`.\n\n"
            "## Source-backed hypothesis attempt\n\n"
            f"{r['analyst_rationale']}\n\n"
            "## What runtime evidence would be required\n\n"
            "A falsifiable runtime check could not be specified from source alone for this candidate (see rationale). "
            "Resolving it would require execution-backed evidence — e.g. a fork/local deployment plus a differential "
            "or invariant test across the cross-contract boundary named above — not further source reasoning. Absent "
            "that, the truthful terminal is "
            f"`{r['terminal_state']}`; no exploit is claimed and no finding is promoted.\n")


def _runtime_md(r: Dict[str, Any]) -> str:
    rt = r["stages"]["C_runtime"]
    return ("# Runtime attempt\n\n"
            f"- Attempted: {rt['attempted']}\n- State: {rt['state']}\n- Reason: {rt.get('reason','')}\n\n"
            "No runtime confirmation was produced, so (per the hard boundaries) no submission package and no "
            "human-review-ready state were created. Nothing is submitted; no severity is assigned.\n")


def write_bundle(sel: Dict[str, Any], r: Dict[str, Any], out_dir: Path) -> Dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "candidate_selection.md").write_text(_selection_md(sel), encoding="utf-8")
    (out_dir / "selection.json").write_text(json.dumps(sel, indent=2) + "\n", encoding="utf-8")
    (out_dir / "intake.json").write_text(json.dumps(r["stages"]["A_intake"], indent=2) + "\n", encoding="utf-8")
    (out_dir / "validation_decision.json").write_text(
        json.dumps(r["stages"]["B_validation"], indent=2) + "\n", encoding="utf-8")
    HP.write_bundle(r["_prep"], out_dir=out_dir / "harness_prep")
    (out_dir / "minimal_reproduction.md").write_text(_minimal_repro_md(r), encoding="utf-8")
    (out_dir / "runtime_attempt.md").write_text(_runtime_md(r), encoding="utf-8")
    (out_dir / "runtime_result.json").write_text(
        json.dumps({"terminal_state": r["terminal_state"], "runtime": r["stages"]["C_runtime"],
                    "safety": r["safety"], "overall_truthful": r["overall_truthful"]}, indent=2) + "\n",
        encoding="utf-8")
    (out_dir / "dry_run_report.md").write_text(_report_md(r), encoding="utf-8")
    return {"dir": str(out_dir)}


# ---------------------------------------------------------------------------- self-test

# the genuine analyst rationale from reading RamsesV3Pool.swap (used by --run; passed in for self-test fixtures)
SWAP_RATIONALE = (
    "Read RamsesV3Pool.swap (the 973-line core UniV3-fork AMM swap). It is the canonical concentrated-liquidity "
    "swap loop plus Ramses' period/secondsPerLiquidity accounting. Observations: (1) the period-rollover writes "
    "(periods[], endSecondsPerLiquidityPeriodX128, lastTick) execute BEFORE the reentrancy lock check and "
    "`slot0.unlocked=false` — unusual vs canonical UniV3 where the lock is first — but the block only writes period "
    "METADATA from a memory snapshot, guarded by `period != lastPeriod`, with no fund movement; (2) the protocol-fee "
    "and feeGrowth math follow the standard pattern; (3) the period machinery this function maintains is exactly what "
    "underlies the real awarded P93 finding (GaugeV3 skipped-period reward inflation), whose IMPACT materializes "
    "cross-contract in GaugeV3's reward computation, not in swap itself. I could NOT form a source-provable exploit "
    "counterexample on swap alone, and could NOT prove it safe: establishing or refuting the reward-inflation path "
    "requires tracing across the in-scope pool->gauge boundary plus runtime evidence (the exact P93 source-only "
    "ceiling). I did not fabricate a trace. Truthful terminal: NEEDS_CONTEXT — high rank (max value/external-call/"
    "state signals on the busiest function) did not, and must not, become a finding.")


def _self_test() -> int:
    ok = True

    def chk(cond, m):
        nonlocal ok
        ok &= bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {m}")

    chk(FLAGS["is_gate"] is False and FLAGS["routes_in_production"] is False, "FLAGS un-wired")

    corpus = json.loads(DEFAULT_CORPUS.read_text(encoding="utf-8")) if DEFAULT_CORPUS.is_file() else None
    if corpus is None:
        print("  [SKIP] corpus absent")
        print("SELF-TEST:", "OK" if ok else "FAILED")
        return 0 if ok else 1

    sel = select_candidate(corpus)
    c = sel["candidate"]
    chk(c is not None, "a candidate is selected")
    chk((c["subject"], c["contract"], c["function"]) not in CONFIRMED_CONTROLS, "selection excludes confirmed controls")
    chk(c["subject"] == "ramses-2024-10" and c["function"] == "swap", "deterministic selection -> RamsesV3Pool.swap")
    # determinism
    chk(json.dumps(sel, sort_keys=True) == json.dumps(select_candidate(corpus), sort_keys=True), "selection deterministic")

    # honest run: no analyst evidence -> NEEDS_CONTEXT terminal
    r = run(c, analyst_evidence=None, analyst_rationale=SWAP_RATIONALE)
    chk(r["terminal_state"] == NEEDS_CONTEXT, "no source-backed evidence -> NEEDS_CONTEXT")
    chk(r["stages"]["B_validation"]["decision"] in ("NEEDS_MORE_CONTEXT", "NEEDS_CONTEXT"), "validator -> needs context")
    chk(r["terminal_state"] in TERMINALS, "terminal in allowed set")
    chk(all(r["safety"].values()), "all safety boundaries hold")
    chk(r["overall_truthful"], "overall truthful")

    # no package / no READY anywhere in the serialized result
    blob = json.dumps({k: v for k, v in r.items() if k != "_prep"})
    chk(not any(t in blob for t in LEAK_TOKENS), "no auto-submit / SUBMITTED token")
    chk("submission_package" not in blob.lower() and "ready_for_human_review" not in blob.lower(),
        "no submission package / READY emitted at NEEDS_CONTEXT")

    # synthetic VALIDATED-but-no-harness -> HARNESS_UNAVAILABLE (no runtime_runner)
    GT = {"localized_mechanism": "x", "controlled_inputs": "x", "pre_state": "x", "operation_trace": "x",
          "boundary_cases": "x", "post_state": "x", "concrete_outcome": "PASS"}
    GO = {"relied_upon_invariant": "x", "mechanism_class": "accounting", "counterexample_found": True,
          "counterexample_trace": "x"}
    GI = {"impact_class": "medium", "proven_magnitude": "significant", "source_true": True, "source_backed": True,
          "material_consequence": ["fund_loss"]}
    rv = run(c, analyst_evidence={"depth_trace": GT, "adversarial_ordering": GO, "impact_assessment": GI},
             analyst_rationale="synthetic")
    chk(rv["stages"]["B_validation"]["decision"] == V.VALIDATED, "synthetic evidence -> VALIDATED")
    chk(rv["terminal_state"] == HARNESS_UNAVAILABLE, "validated but no runner -> HARNESS_UNAVAILABLE (no package)")
    chk(all(rv["safety"].values()), "validated-path safety holds (no package/READY without runtime)")

    # synthetic VALIDATED + a runtime_runner that confirms -> CONFIRMED_RUNTIME (only path to a package)
    rc = run(c, analyst_evidence={"depth_trace": GT, "adversarial_ordering": GO, "impact_assessment": GI},
             analyst_rationale="synthetic", runtime_runner=lambda cand, prep: {"confirmed": True, "killed": False,
             "state": "CONFIRMED", "reason": "stub run", "evidence": "stub"})
    chk(rc["terminal_state"] == CONFIRMED_RUNTIME and rc["stages"]["C_runtime"]["attempted"],
        "validated + confirming runner -> CONFIRMED_RUNTIME (execution-backed)")

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
        corpus_path = args.corpus or str(DEFAULT_CORPUS)
        corpus = json.loads(Path(corpus_path).read_text(encoding="utf-8"))
        sel = select_candidate(corpus)
        # honest run on the mechanically-selected candidate: NO fabricated evidence (analyst_evidence=None)
        r = run(sel["candidate"], analyst_evidence=None, analyst_rationale=SWAP_RATIONALE, corpus_path=corpus_path)
        out = write_bundle(sel, r, Path(args.out_dir) if args.out_dir else DEFAULT_OUT)
        c = sel["candidate"]
        print(f"P113 fresh discovery — candidate {c['subject']}::{c['contract']}.{c['function']} "
              f"(score {c['score']})")
        print(f"  terminal: {r['terminal_state']}  ·  validation: {r['stages']['B_validation']['decision']}  ·  "
              f"harness: {r['stages']['C0_harness_prep']['classification']}")
        print(f"  safety: {r['safety']}")
        print(f"  overall_truthful: {r['overall_truthful']}")
        print(f"  -> {out['dir']}")
        return 0 if r["overall_truthful"] else 1
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
