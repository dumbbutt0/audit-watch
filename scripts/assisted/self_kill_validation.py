#!/usr/bin/env python3
"""P108 — Adversarial self-kill validation (research-only, UN-WIRED).
"Self-kill exists to challenge candidates, not to approve them. A survivor is merely worthy of further investigation."

Every candidate enters as FALSE and must survive attempts to kill it. The layer attempts to invalidate each candidate
using the strongest SOURCE-BACKED counterarguments available (the frozen map_invariant_defenses is the defense /
counterexample engine; the P106/P107 features are the exploit thesis). The goal is to ELIMINATE weak candidates
before human time is spent — not to find or approve bugs.

Deterministic + source-derived (no LLM, no API). Conservative by construction: it kills only when a defense is
PROVABLE from source (a dispositive guard, or full coverage with no exploit consequence). It never kills a candidate
whose dispute needs runtime (-> NEEDS_RUNTIME) and never kills a confirmed-reproduced candidate (-> SURVIVED). This
keeps real (awarded) findings and the P104 PoC alive — the hard-stop the spec requires.

Scope: top-K of the P107 RECOMMENDED ranking + the known-confirmed P104 candidate + the historical awarded findings
(ground truth). NOT the whole enumerated surface.

States (the ONLY outputs): KILLED · SURVIVED · NEEDS_RUNTIME · NEEDS_CONTEXT.
NON-NEGOTIABLE: no detector/threshold/severity change, no report/submission/validation/funnel/PoC-lock state.

Usage:
    python scripts/assisted/self_kill_validation.py --self-test
    python scripts/assisted/self_kill_validation.py --run    # -> p108/{self_kill_results,self_kill_report,ground_truth_report}
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

import rank_candidates_prototype as RANK   # noqa: E402  (P107; read-only — recommended ranking)
import rank_signal_probe as PROBE          # noqa: E402  (P106; read-only — bodies/features)
import benchmark_replay as BENCH           # noqa: E402  (P105; read-only — _resolve_sol_files)
import map_invariant_defenses as DEF       # noqa: E402  (frozen defense engine)
import enumerate_candidate_invariants as ENUM  # noqa: E402

FLAGS = {
    "is_gate": False,
    "research_only": True,
    "review_only": True,
    "routes_in_production": False,
    "routed_manifest_ids": [],
}

DEFAULT_CORPUS = ROOT / "documentation" / "research" / "assisted_mode" / "p105" / "benchmark_corpus.json"
DEFAULT_OUT = ROOT / "documentation" / "research" / "assisted_mode" / "p108"

# the FOUR (and only) candidate states
KILLED, SURVIVED, NEEDS_RUNTIME, NEEDS_CONTEXT = "KILLED", "SURVIVED", "NEEDS_RUNTIME", "NEEDS_CONTEXT"
STATES = {KILLED, SURVIVED, NEEDS_RUNTIME, NEEDS_CONTEXT}
FORBIDDEN_TOKENS = ("severity", "submission", "report_ready", "submission_ready", "poc_lock", "SUBMITTED",
                    "validated_for_poc", "predicted_severity")

# a "sharp consequence" = a real impact path (state_write_breadth is near-universal, so it is NOT a consequence)
_CONSEQUENCE = ("consequence_value_movement", "consequence_fund_reachability", "exploitability_external_call")


@lru_cache(maxsize=1)
def _cfg() -> Dict[str, Any]:
    return {"top_k": 10, "ranking_variant": "recommended"}


# ---------------------------------------------------------------------------- candidate assembly

def _bodies_for(spec: Dict[str, Any], excludes: List[str]) -> Dict[Tuple[str, str], str]:
    bodies: Dict[Tuple[str, str], str] = {}
    for f in BENCH._resolve_sol_files(spec.get("source_roots", []), excludes):
        try:
            bodies.update(PROBE._function_bodies(f.read_text(encoding="utf-8")))
        except (OSError, UnicodeDecodeError):
            continue
    return bodies


def assemble_candidates(corpus: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Scope per spec: top-K recommended per subject + every awarded finding + the confirmed P104 candidate.
    Each candidate carries its body, features, declared/derived category, and any confirmed-PoC evidence."""
    excludes = corpus.get("exclude_substrings", [])
    surfaces = RANK._surfaces(corpus)
    rec_feats = RANK.VARIANTS["recommended"] if "recommended" in RANK.VARIANTS else \
        ["consequence_value_movement", "consequence_fund_reachability", "exploitability_external_call",
         "state_write_breadth"]
    K = _cfg()["top_k"]

    awarded_keys: Dict[str, set] = {}
    awarded_meta: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
    for spec in corpus["subjects"]:
        awarded_keys[spec["id"]] = set()
        for fnd in spec.get("awarded_findings", []):
            if not fnd.get("surfaceable"):
                continue
            awarded_keys[spec["id"]].add((fnd["contract"], fnd["function"]))
            awarded_meta[(spec["id"], fnd["contract"], fnd["function"])] = fnd

    cands: Dict[Tuple[str, str, str], Dict[str, Any]] = {}

    def _mk(sid, contract, fn, rank, features, bodies, source):
        key = (sid, contract, fn)
        if key in cands:
            cands[key]["sources"].append(source)
            return
        meta = awarded_meta.get(key)
        conv = (meta or {}).get("conversion") or {}
        cands[key] = {
            "subject": sid, "contract": contract, "function": fn, "rank": rank,
            "body": bodies.get((contract, fn), ""),
            "features": features,
            "declared_category": (meta or {}).get("invariant_category"),
            "is_awarded": meta is not None,
            "is_confirmed_poc": bool(conv.get("poc_succeeded")),
            "conversion_ref": conv.get("evidence_ref"),
            "sources": [source],
        }

    for spec in corpus["subjects"]:
        sid = spec["id"]
        surface = surfaces[sid]["surface"]
        bodies = _bodies_for(spec, excludes)
        ranked = RANK.rank_surface(surface, rec_feats)
        # 1) top-K of the recommended ranking
        for r in ranked[:K]:
            feats = surface[(r["contract"], r["function"])]["features"]
            _mk(sid, r["contract"], r["function"], r["rank"], feats, bodies,
                "awarded_topk" if (r["contract"], r["function"]) in awarded_keys[sid] else "ranked_topk")
        # 2) every awarded finding (ground truth) even if it ranked below K
        for (contract, fn) in awarded_keys[sid]:
            rec = next((x for x in ranked if x["contract"] == contract and x["function"] == fn), None)
            feats = surface.get((contract, fn), {}).get("features", {})
            _mk(sid, contract, fn, rec["rank"] if rec else None, feats, bodies, "awarded_groundtruth")
    return list(cands.values())


# ---------------------------------------------------------------------------- the six stages

def _strongest_defense(body: str, categories: List[str]) -> Dict[str, Any]:
    """Stage 2 — assume the candidate is WRONG; find the strongest source-backed defense across plausible categories."""
    order = {DEF.COVERS: 3, DEF.PARTIALLY_COVERS: 2, DEF.DOES_NOT_COVER: 1, DEF.UNKNOWN_NEEDS_TRACE: 0}
    best, best_cat, needs_trace = DEF.DOES_NOT_COVER, None, False
    per_cat = {}
    for cat in categories:
        cov = DEF.map_defenses({"invariant_type": cat}, body)["coverage"]
        per_cat[cat] = cov
        if cov == DEF.UNKNOWN_NEEDS_TRACE:
            needs_trace = True
        if order[cov] > order[best]:
            best, best_cat = cov, cat
    dispositive = bool(DEF._PRIMS["buyer_seller_guard"].search((body or "").lower()))
    # a kill-grade COVERS must come from a category with >=2 relevant primitives ALL present — a single-primitive
    # category (negative_space / cross_contract) reaching "COVERS" off one coincidental match is NOT proof.
    multi_primitive = bool(best == DEF.COVERS and best_cat is not None
                           and len(DEF._RELEVANT.get(best_cat, [])) >= 2)
    return {"strongest_coverage": best, "covering_category": best_cat,
            "needs_trace": needs_trace, "dispositive_guard": dispositive,
            "covering_multi_primitive": multi_primitive, "per_category": per_cat}


def self_kill(candidate: Dict[str, Any]) -> Dict[str, Any]:
    body = candidate.get("body") or ""
    feats = candidate.get("features") or {}
    name = candidate["function"]

    # categories the exploit could rely on: enumerate-fired + the declared (awarded) category, if any
    fired = [c["invariant_type"] for c in ENUM.enumerate_invariants({"function": name, "source_text": body})
             ["candidate_invariants"]] if body.strip() else []
    cats = sorted(set(fired) | ({candidate["declared_category"]} if candidate.get("declared_category") else set()))

    sharp = [s for s in _CONSEQUENCE if feats.get(s, 0.0) > 0]
    permissionless = feats.get("actor_clarity", 0.0) > 0
    external = feats.get("exploitability_external_call", 0.0) > 0

    # Stage 1 — exploit thesis (strongest source-backed claim)
    exploit = {
        "violated_invariant": candidate.get("declared_category") or (cats[0] if cats else "value_conservation"),
        "attacker_path": "permissionless EOA entrypoint" if permissionless else "requires a privileged principal",
        "expected_consequence": sharp or ["no sharp consequence signal (impact unclear from surface)"],
        "assumptions": (["the external-call boundary behaves adversarially"] if external else [])
                       + ([] if body.strip() else ["function body resolvable from in-scope source"]),
    }
    # Stage 2 — defense thesis (assume wrong)
    defense = _strongest_defense(body, cats)
    # Stage 3 — counterexample search (deterministic: a proven defense IS the counterexample)
    counterexample = None
    if defense["dispositive_guard"]:
        counterexample = "a dispositive guard (buyer!=seller / direct principal check) blocks the attacker path"
    elif defense["strongest_coverage"] == DEF.COVERS and defense["covering_multi_primitive"] and not sharp:
        counterexample = ("a multi-guard defense fully covers the invariant and the function exposes no "
                          "value/fund/external consequence")
    # Stage 4 — adversarial interpretation
    adversarial = []
    if not permissionless:
        adversarial.append("admin-only / privileged-principal behavior (not an open attacker path)")
    if not sharp:
        adversarial.append("missing economic consequence (no value movement / fund reachability / external call)")
    if defense["strongest_coverage"] in (DEF.COVERS, DEF.PARTIALLY_COVERS):
        adversarial.append(f"intended-behavior reading: source-level defense {defense['strongest_coverage']}")
    # Stage 5 — runtime requirement (source cannot resolve the dispute)
    runtime_required = bool((external or defense["needs_trace"]) and counterexample is None)

    # Stage 6 — decision (precedence; conservative)
    if candidate.get("is_confirmed_poc"):
        state, reason = SURVIVED, "confirmed reproduced PoC — self-kill cannot kill a proven exploit"
    elif not body.strip():
        state, reason = NEEDS_CONTEXT, "insufficient source: function body not resolvable from in-scope source"
    elif counterexample is not None:
        state, reason = KILLED, f"defense proven from source: {counterexample}"
    elif runtime_required:
        state, reason = NEEDS_RUNTIME, ("source analysis exhausted: cross-contract / boundary value must be traced "
                                        "at runtime to resolve exploit-vs-defense")
    else:
        state, reason = SURVIVED, ("exploit thesis intact: source-backed consequence remains and no source-provable "
                                   "kill path was found")

    return {
        "subject": candidate["subject"], "contract": candidate["contract"], "function": candidate["function"],
        "rank": candidate.get("rank"), "is_awarded": candidate.get("is_awarded", False),
        "is_confirmed_poc": candidate.get("is_confirmed_poc", False),
        "state": state, "reason": reason,
        "exploit_thesis": exploit, "defense_thesis": defense,
        "counterexample": counterexample, "adversarial_interpretation": adversarial,
        "runtime_required": runtime_required,
        # provenance of the kill (used by hard-stop checks): a KILL must be defense-proven, never uncertainty
        "kill_basis": ("dispositive_guard" if (state == KILLED and defense["dispositive_guard"])
                       else ("covered_and_inert" if state == KILLED else None)),
    }


# ---------------------------------------------------------------------------- corpus run + metrics

def run_corpus(corpus: Dict[str, Any]) -> Dict[str, Any]:
    candidates = assemble_candidates(corpus)
    results = [self_kill(c) for c in candidates]

    awarded = [r for r in results if r["is_awarded"]]
    presumed_weak = [r for r in results if not r["is_awarded"]]   # non-awarded top-K (kill targets)
    p104 = [r for r in results if r["is_confirmed_poc"]]

    def _count(rs):
        return {s: sum(1 for r in rs if r["state"] == s) for s in (KILLED, SURVIVED, NEEDS_RUNTIME, NEEDS_CONTEXT)}

    n = len(results)
    killed = sum(1 for r in results if r["state"] == KILLED)
    survived = sum(1 for r in results if r["state"] == SURVIVED)
    metrics = {
        "total_candidates": n,
        "by_state": _count(results),
        "killed": killed, "survived": survived,
        "needs_runtime": sum(1 for r in results if r["state"] == NEEDS_RUNTIME),
        "needs_context": sum(1 for r in results if r["state"] == NEEDS_CONTEXT),
        "survival_rate": round(survived / n, 4) if n else None,
        "kill_rate": round(killed / n, 4) if n else None,
        "rank_distribution": {
            "killed_ranks": sorted(r["rank"] for r in results if r["state"] == KILLED and r["rank"] is not None),
            "survived_ranks": sorted(r["rank"] for r in results if r["state"] == SURVIVED and r["rank"] is not None),
        },
        "known_good": {
            "n": len(awarded), "by_state": _count(awarded),
            "survival_rate": round(sum(1 for r in awarded if r["state"] in (SURVIVED, NEEDS_RUNTIME, NEEDS_CONTEXT))
                                   / len(awarded), 4) if awarded else None,
            "killed": [f"{r['subject']}:{r['function']}" for r in awarded if r["state"] == KILLED],
        },
        "presumed_weak_non_awarded": {
            "n": len(presumed_weak), "by_state": _count(presumed_weak),
            "kill_rate": round(sum(1 for r in presumed_weak if r["state"] == KILLED) / len(presumed_weak), 4)
            if presumed_weak else None,
        },
    }

    ground_truth = {
        "p104_state": (p104[0]["state"] if p104 else "ABSENT"),
        "confirmed_pocs": [{"function": r["function"], "state": r["state"]} for r in p104],
        "awarded_killed": metrics["known_good"]["killed"],
        "awarded_killed_count": len(metrics["known_good"]["killed"]),
        "awarded_total": len(awarded),
        "awarded_survived_or_held": sum(1 for r in awarded if r["state"] != KILLED),
    }

    hard_stops = _hard_stops(results, metrics, ground_truth)
    verdict = _verdict(metrics, ground_truth, hard_stops)

    return {
        **FLAGS,
        "schema": "p108_self_kill_results_v1",
        "invariant": "Self-kill exists to challenge candidates, not to approve them. A survivor is merely worthy of "
                     "further investigation.",
        "note": ("Deterministic source-derived adversarial self-kill over the P107 top-K recommended ranking + "
                 "awarded ground truth + the P104 confirmed candidate. Conservative: kills only on a source-provable "
                 "defense; cross-contract -> NEEDS_RUNTIME; confirmed PoC -> SURVIVED. No severity / report / "
                 "submission / validation / funnel / PoC-lock state."),
        "config": _cfg(),
        "metrics": metrics, "ground_truth": ground_truth,
        "hard_stops": hard_stops, "verdict": verdict,
        "candidates": results,
    }


def _hard_stops(results, metrics, gt) -> Dict[str, Any]:
    killed = [r for r in results if r["state"] == KILLED]
    hs = {}
    hs["HS_p104_killed"] = {"tripped": gt["p104_state"] == KILLED}
    hs["HS_majority_awarded_killed"] = {"tripped": gt["awarded_killed_count"] * 2 > gt["awarded_total"],
                                        "killed": gt["awarded_killed_count"], "of": gt["awarded_total"]}
    # kill rate exceeds survival rate SOLELY due to uncertainty: every KILL must be defense-proven (kill_basis set)
    kills_without_basis = [f"{r['subject']}:{r['function']}" for r in killed if not r.get("kill_basis")]
    hs["HS_kill_by_uncertainty"] = {"tripped": bool(kills_without_basis), "kills_without_defense_basis": kills_without_basis}
    # runtime-required mislabeled as killed
    rt_mislabeled = [f"{r['subject']}:{r['function']}" for r in killed if r.get("runtime_required")]
    hs["HS_runtime_mislabeled_as_killed"] = {"tripped": bool(rt_mislabeled), "cases": rt_mislabeled}
    # new/forbidden states or fields
    bad_states = sorted({r["state"] for r in results} - STATES)
    blob = json.dumps(results)
    forbidden = [t for t in FORBIDDEN_TOKENS if t in blob]
    hs["HS_new_states_or_fields"] = {"tripped": bool(bad_states or forbidden),
                                     "bad_states": bad_states, "forbidden_tokens": forbidden}
    return hs


def _verdict(metrics, gt, hard_stops) -> Dict[str, Any]:
    any_hs = any(h["tripped"] for h in hard_stops.values())
    weak_eliminated = (metrics["presumed_weak_non_awarded"]["kill_rate"] or 0) > 0
    strong_survive = gt["awarded_killed_count"] == 0
    p104_survives = gt["p104_state"] == SURVIVED
    precision_up_recall_kept = weak_eliminated and strong_survive
    # SAFETY (does the layer avoid harm?) is separable from KILL POWER (does it eliminate weak candidates?).
    safety_pass = bool(strong_survive and p104_survives and not any_hs)
    kill_power_pass = bool(weak_eliminated)
    if safety_pass and kill_power_pass:
        conclusion = "PASS — self-kill safely eliminates weak candidates while sparing real findings."
    elif safety_pass and not kill_power_pass:
        conclusion = ("SAFETY PASS / KILL-POWER FAIL — source-only self-kill is correctly conservative (0 awarded "
                      "killed, P104 survives, no hard stop) but cannot eliminate any top-K candidate from source "
                      "alone: top-K is selected for looking exploitable, and every source signal that would kill a "
                      "weak candidate also hits an awarded one (exploitable views/role-guarded findings). The "
                      f"{metrics['needs_runtime']} NEEDS_RUNTIME candidates show the dispute is runtime-bound — "
                      "elimination must come from RUNTIME execution (attempt the exploit), not more source heuristics.")
    else:
        conclusion = "FAIL — safety hard-stop tripped (a real finding or P104 was killed)."
    return {
        "weak_candidates_eliminated": weak_eliminated,
        "strong_historical_survive": strong_survive,
        "p104_survives": p104_survives,
        "precision_up_without_recall_harm": precision_up_recall_kept,
        "no_hard_stop_tripped": not any_hs,
        "safety_pass": safety_pass,
        "kill_power_pass": kill_power_pass,
        "overall_pass": bool(safety_pass and kill_power_pass),
        "conclusion": conclusion,
    }


# ---------------------------------------------------------------------------- reports

def render_self_kill_report(res: Dict[str, Any]) -> str:
    m, v = res["metrics"], res["verdict"]
    L = ["# P108 — Adversarial self-kill: results", "",
         f"**Invariant:** {res['invariant']}  ·  research-only, un-wired.",
         f"Scope: top-{res['config']['top_k']} of the P107 `{res['config']['ranking_variant']}` ranking + awarded "
         f"ground truth + the P104 confirmed candidate.", "",
         "## Verdict",
         f"- **SAFETY PASS: {v['safety_pass']}**  ·  **KILL-POWER PASS: {v['kill_power_pass']}**  ·  "
         f"**OVERALL PASS: {v['overall_pass']}**",
         f"- {v['conclusion']}",
         f"- weak eliminated: {v['weak_candidates_eliminated']} · strong survive: {v['strong_historical_survive']} · "
         f"P104 survives: {v['p104_survives']} · precision↑ w/o recall harm: "
         f"{v['precision_up_without_recall_harm']} · no hard stop: {v['no_hard_stop_tripped']}", "",
         "## Metrics",
         f"- total candidates: **{m['total_candidates']}**  ·  by state: {m['by_state']}",
         f"- kill_rate: {m['kill_rate']} · survival_rate: {m['survival_rate']}",
         f"- presumed-weak (non-awarded top-K): n={m['presumed_weak_non_awarded']['n']}, "
         f"kill_rate={m['presumed_weak_non_awarded']['kill_rate']}, by_state={m['presumed_weak_non_awarded']['by_state']}",
         f"- known-good (awarded): n={m['known_good']['n']}, survival(incl needs_*)={m['known_good']['survival_rate']}, "
         f"killed={m['known_good']['killed'] or 'none'}",
         f"- killed ranks: {m['rank_distribution']['killed_ranks']}", "",
         "## Hard stops"]
    for name, h in res["hard_stops"].items():
        L.append(f"- **{name}** — tripped: {h['tripped']}" + (f"  {({k: v2 for k, v2 in h.items() if k != 'tripped'})}"
                                                              if len(h) > 1 else ""))
    L += ["", "## Candidate states (KILLED / NEEDS_RUNTIME / NEEDS_CONTEXT shown; survivors summarised)", "",
          "| Subject | Contract.fn | rank | awarded | state | basis/reason |", "|---|---|---|---|---|---|"]
    for r in sorted(res["candidates"], key=lambda x: (x["state"], x["subject"], x["function"])):
        if r["state"] == SURVIVED and not r["is_awarded"]:
            continue  # keep the table focused; full data in JSON
        L.append(f"| {r['subject']} | {r['contract']}.{r['function']} | {r['rank']} | "
                 f"{'Y' if r['is_awarded'] else ''} | {r['state']} | {(r['kill_basis'] or r['reason'])[:60]} |")
    L += ["", "## Reading",
          "- KILLED requires a source-PROVABLE defense (dispositive guard, or full coverage with no consequence). "
          "Uncertainty is never a kill — it is NEEDS_RUNTIME / NEEDS_CONTEXT.",
          "- Survivors are NOT validated/approved — only 'worth further investigation'.", ""]
    return "\n".join(L) + "\n"


def render_ground_truth_report(res: Dict[str, Any]) -> str:
    gt, hs = res["ground_truth"], res["hard_stops"]
    L = ["# P108 — Ground-truth report", "",
         "The self-kill layer must spare real findings. It FAILS if it kills P104 or a majority of awarded findings.",
         "", "## Confirmed PoC (P104)",
         f"- IQ-AI M-01 state: **{gt['p104_state']}** (required: SURVIVED)",
         f"- HS_p104_killed tripped: {hs['HS_p104_killed']['tripped']}", "",
         "## Awarded findings (known-good real bugs)",
         f"- total awarded: {gt['awarded_total']}",
         f"- awarded KILLED: {gt['awarded_killed_count']} {gt['awarded_killed'] or ''}",
         f"- awarded survived/held (not killed): {gt['awarded_survived_or_held']}",
         f"- HS_majority_awarded_killed tripped: {hs['HS_majority_awarded_killed']['tripped']}", "",
         "## Per-awarded state"]
    L.append("| Subject | finding fn | state |")
    L.append("|---|---|---|")
    for r in sorted([c for c in res["candidates"] if c["is_awarded"]], key=lambda x: x["subject"]):
        L.append(f"| {r['subject']} | {r['function']} | {r['state']} |")
    L += ["", "## Conclusion",
          f"- The layer {'PRESERVES' if gt['awarded_killed_count'] == 0 else 'KILLS SOME OF'} the awarded findings "
          f"and {'KEEPS' if gt['p104_state'] == SURVIVED else 'KILLS'} P104.",
          "- Honest residual: awarded findings landing in NEEDS_RUNTIME are the cross-contract / runtime-bound class "
          "(source-only self-kill correctly declines to judge them).", ""]
    return "\n".join(L) + "\n"


def write_outputs(res: Dict[str, Any], out_dir: Path) -> Dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    rj = out_dir / "self_kill_results.json"
    rr = out_dir / "self_kill_report.md"
    gr = out_dir / "ground_truth_report.md"
    rj.write_text(json.dumps(res, indent=2) + "\n", encoding="utf-8")
    rr.write_text(render_self_kill_report(res), encoding="utf-8")
    gr.write_text(render_ground_truth_report(res), encoding="utf-8")
    return {"results": str(rj), "report": str(rr), "ground_truth": str(gr)}


def assert_states_only(res: Dict[str, Any]) -> bool:
    states_ok = all(r["state"] in STATES for r in res["candidates"])
    blob = json.dumps(res["candidates"])
    no_forbidden = not any(t in blob for t in FORBIDDEN_TOKENS)
    return states_ok and no_forbidden


# ---------------------------------------------------------------------------- self-test

_FIXTURE = (
    "// SPDX-License-Identifier: MIT\npragma solidity ^0.8.0;\n"
    "contract C {\n"
    "  mapping(address=>uint256) public bal; uint256 public total; address owner; address seller;\n"
    "  // real-bug shape: permissionless, moves value, no covering guard -> must SURVIVE\n"
    "  function withdrawAll() external { bal[msg.sender]+=1; total+=1; IERC20(t).transfer(msg.sender, total); }\n"
    "  // dispositive guard (buyer!=seller) + role check -> KILLED (defense proven)\n"
    "  function buy(uint256 id) external { require(msg.sender != seller, \"no self buy\"); bal[msg.sender]+=id; }\n"
    "  // cross-contract: value depends on an external call -> NEEDS_RUNTIME\n"
    "  function sync() external { uint256 p = IOracle(o).price(); total = p; pool.staticcall(d); }\n"
    "  // fully covered (cap_limit: require(<= limit)) + inert (no value/fund/external) -> KILLED (covered_and_inert)\n"
    "  function poke(uint256 x) external { require(x <= limit); cfg = x; }\n"
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
    tmp = Path(tempfile.mkdtemp(prefix="p108_selftest_"))
    (tmp / "C.sol").write_text(_FIXTURE, encoding="utf-8")
    corpus = {
        "exclude_substrings": [],
        "subjects": [{
            "id": "fx", "phase": "self-test", "source_roots": [str(tmp)],
            "awarded_findings": [
                {"finding_id": "AWD", "contract": "C", "function": "withdrawAll",
                 "invariant_category": "per_user_accounting", "severity": "High",
                 "surfaceable": True, "grounding": "high"},
                {"finding_id": "AWD-XC", "contract": "C", "function": "sync",
                 "invariant_category": "cross_contract_consistency", "severity": "Medium",
                 "surfaceable": True, "grounding": "high",
                 "conversion": {"poc_succeeded": True, "evidence_ref": "fixture-confirmed"}},
            ],
        }],
    }
    res = run_corpus(corpus)
    res2 = run_corpus(corpus)
    for p in tmp.glob("*"):
        p.unlink()
    tmp.rmdir()

    by_fn = {r["function"]: r for r in res["candidates"]}
    chk(by_fn["buy"]["state"] == KILLED and by_fn["buy"]["kill_basis"] == "dispositive_guard",
        "dispositive buyer!=seller guard -> KILLED")
    chk(by_fn["poke"]["state"] == KILLED and by_fn["poke"]["kill_basis"] == "covered_and_inert",
        "guarded + no consequence -> KILLED (covered_and_inert)")
    chk(by_fn["withdrawAll"]["state"] == SURVIVED, "permissionless value-moving real-bug shape -> SURVIVED")
    chk(by_fn["sync"]["state"] == SURVIVED, "confirmed-PoC candidate (sync) -> SURVIVED (never killed)")
    chk(by_fn["sync"]["is_confirmed_poc"], "PoC candidate flagged confirmed")

    # a NON-confirmed cross-contract function would be NEEDS_RUNTIME — verify via a fresh candidate w/o poc
    plain_sync = self_kill({"subject": "x", "contract": "C", "function": "sync2",
                            "body": "function sync2() external { uint256 p = IOracle(o).price(); total=p; pool.staticcall(d); }",
                            "features": {"exploitability_external_call": 1.0, "actor_clarity": 1.0},
                            "declared_category": "cross_contract_consistency", "is_awarded": False,
                            "is_confirmed_poc": False})
    chk(plain_sync["state"] == NEEDS_RUNTIME, "cross-contract, unconfirmed -> NEEDS_RUNTIME")

    empty = self_kill({"subject": "x", "contract": "C", "function": "ghost", "body": "",
                       "features": {}, "is_awarded": False, "is_confirmed_poc": False})
    chk(empty["state"] == NEEDS_CONTEXT, "no body -> NEEDS_CONTEXT")

    chk(all(r["state"] in STATES for r in res["candidates"]), "only the 4 allowed states emitted")
    chk(assert_states_only(res), "no forbidden severity/submission/validation tokens")
    chk(res["ground_truth"]["awarded_killed_count"] == 0, "no awarded finding killed in fixture")
    chk(res["hard_stops"]["HS_p104_killed"]["tripped"] is False, "P104-style confirmed not killed")
    chk(res["hard_stops"]["HS_runtime_mislabeled_as_killed"]["tripped"] is False, "no runtime case mislabeled killed")
    chk(json.dumps(res, sort_keys=True) == json.dumps(res2, sort_keys=True), "deterministic on re-run")
    chk(res["verdict"]["overall_pass"] is True, "fixture verdict overall_pass")

    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--corpus", help="default: p105/benchmark_corpus.json")
    ap.add_argument("--out-dir", help="default: documentation/research/assisted_mode/p108")
    args = ap.parse_args()

    if args.self_test:
        return _self_test()
    if args.run:
        corpus = json.loads(Path(args.corpus or DEFAULT_CORPUS).read_text(encoding="utf-8"))
        res = run_corpus(corpus)
        if not assert_states_only(res):
            print("ABORT: forbidden state/field in output.", file=sys.stderr)
            return 2
        out = write_outputs(res, Path(args.out_dir) if args.out_dir else DEFAULT_OUT)
        m, v, gt = res["metrics"], res["verdict"], res["ground_truth"]
        print(f"P108 self-kill — OVERALL PASS={v['overall_pass']}")
        print(f"  total={m['total_candidates']} by_state={m['by_state']}")
        print(f"  presumed-weak kill_rate={m['presumed_weak_non_awarded']['kill_rate']} "
              f"(n={m['presumed_weak_non_awarded']['n']})")
        print(f"  awarded killed={gt['awarded_killed_count']}/{gt['awarded_total']}  P104={gt['p104_state']}")
        print(f"  hard_stops tripped: {{k: h['tripped'] for k,h in res['hard_stops'].items()}}".replace(
            "{k: h['tripped'] for k,h in res['hard_stops'].items()}",
            str({k: h['tripped'] for k, h in res['hard_stops'].items()})))
        print(f"  -> {out['results']}\n  -> {out['report']}\n  -> {out['ground_truth']}")
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
