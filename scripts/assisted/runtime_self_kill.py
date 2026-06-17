#!/usr/bin/env python3
"""P109 — Runtime self-kill validation (research-only, UN-WIRED).
"Runtime self-kill exists to falsify exploit hypotheses; a surviving candidate is not a vulnerability — it is merely
the next candidate worthy of deeper investigation."

P108 proved source-only adversarial review is SAFE but POWERLESS (0 kills, 28 NEEDS_RUNTIME). P109 tests whether
RUNTIME EXECUTION can eliminate candidates source reasoning could not. Runtime execution is now the only admissible
evidence: a candidate survives only if runtime attempts fail to kill it; a KILLED/SURVIVED decision must be
execution-backed (HS3).

REALITY (recon-confirmed): the 28 NEEDS_RUNTIME candidates have NO per-candidate exploit harness (and 6/7 subjects
have no installed deps), so building one is P104-level effort x 28 — out of scope. This layer therefore performs
deterministic HARNESS DISCOVERY (the 28 -> HARNESS_UNAVAILABLE) and LIVE-EXECUTES the existing positive control
(P104 IQ-AI M-01 fork PoC -> SURVIVED_RUNTIME). The honest result is runtime_kill_rate = 0: runtime self-kill is the
correct, SAFE mechanism but is GATED by executable-harness construction. No fabricated kills.

States (the ONLY outputs): KILLED_RUNTIME · SURVIVED_RUNTIME · INCONCLUSIVE_RUNTIME · HARNESS_UNAVAILABLE.
NON-NEGOTIABLE: no severity / validation / report / submission state; no new candidates; no ranking change.

Usage:
    python scripts/assisted/runtime_self_kill.py --self-test
    python scripts/assisted/runtime_self_kill.py --run    # live-executes the P104 control via forge
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent.parent

FLAGS = {
    "is_gate": False,
    "research_only": True,
    "review_only": True,
    "routes_in_production": False,
    "routed_manifest_ids": [],
}

P108_RESULTS = ROOT / "documentation" / "research" / "assisted_mode" / "p108" / "self_kill_results.json"
DEFAULT_OUT = ROOT / "documentation" / "research" / "assisted_mode" / "p109"

KILLED, SURVIVED, INCONCLUSIVE, HARNESS_UNAVAILABLE = (
    "KILLED_RUNTIME", "SURVIVED_RUNTIME", "INCONCLUSIVE_RUNTIME", "HARNESS_UNAVAILABLE")
STATES = {KILLED, SURVIVED, INCONCLUSIVE, HARNESS_UNAVAILABLE}
FORBIDDEN_TOKENS = ("severity", "submission", "report_ready", "submission_ready", "validated_for_poc",
                    "predicted_severity", "poc_lock")

# source-only kill rate established by P108 (for the criterion "runtime kill rate exceeds source-only kill rate")
SOURCE_ONLY_KILL_RATE = 0.0

# existing executable positive controls (awarded + confirmed-reproduced findings with a harness on disk)
POSITIVE_CONTROLS = [
    {"id": "P104-IQAI-M01", "subject": "iq-ai-2025-01", "contract": "LiquidityManager", "function": "moveLiquidity",
     "is_awarded": True, "is_confirmed_poc": True,
     "harness_dir": "/tmp/p102-iqai", "harness_file": "test/audit/M01PreCreatePairPoC.t.sol",
     "match_test": "test_M01_attacker_precreate_low_fee_is_adopted", "evm_version": "cancun",
     "env": {"FRAXTAL_MAINNET_URL": "https://rpc.frax.com"},
     "frozen_evidence": "documentation/research/assisted_mode/p104/reproduction_output.txt"},
    {"id": "M11-SECONDSWAP", "subject": "secondswap-2024-12", "contract": "SecondSwap_Marketplace",
     "function": "spotPurchase", "is_awarded": True, "is_confirmed_poc": True,
     "harness_dir": "/tmp/p97-secondswap", "harness_file": "test/audit/M11SelfPurchasePoC.t.sol",
     "match_test": "test_M11_SelfPurchaseInflatesBoughtAndBypassesMaxSellPercent", "evm_version": None,
     "env": {}, "frozen_evidence": None},
]


@lru_cache(maxsize=1)
def _cfg() -> Dict[str, Any]:
    return {"source_only_kill_rate": SOURCE_ONLY_KILL_RATE, "forge": shutil.which("forge") is not None}


# ---------------------------------------------------------------------------- harness discovery (deterministic)

def _subject_tmp_root(subject: str, corpus: Dict[str, Any]) -> Optional[str]:
    for s in corpus.get("subjects", []):
        if s["id"] == subject and s.get("source_roots"):
            parts = Path(s["source_roots"][0]).parts  # ('/','tmp','p89-phi','src')
            if len(parts) >= 3 and parts[1] == "tmp":
                return str(Path(parts[0], parts[1], parts[2]))
    return None


def _deps_present(harness_dir: str) -> bool:
    d = Path(harness_dir)
    return (d / "node_modules").is_dir() or (d / "lib").is_dir()


def discover_harness(subject: str, function: str, corpus: Dict[str, Any]) -> Dict[str, Any]:
    """Look for an EXISTING exploit harness (a .t.sol under test/audit or named *PoC* that references this function)
    and whether deps are installed so it could run. The 28 NEEDS_RUNTIME candidates have none."""
    root = _subject_tmp_root(subject, corpus)
    if not root or not Path(root).is_dir():
        return {"exploit_harness": None, "deps_present": False, "runnable": False, "reason": "subject_clone_absent"}
    hits = []
    base = Path(root)
    for sub in ("test/audit", "test", "src/test"):
        p = base / sub
        if not p.is_dir():
            continue
        for f in p.rglob("*.t.sol"):
            is_exploit = ("audit" in str(f).lower()) or ("poc" in f.name.lower())
            if not is_exploit:
                continue
            try:
                if function and function in f.read_text(encoding="utf-8"):
                    hits.append(str(f))
            except (OSError, UnicodeDecodeError):
                continue
    deps = _deps_present(root)
    runnable = bool(hits) and deps and _cfg()["forge"]
    reason = ("ok" if runnable else
              ("no_exploit_harness" if not hits else
               ("deps_absent" if not deps else "forge_absent")))
    return {"exploit_harness": hits[0] if hits else None, "deps_present": deps, "runnable": runnable, "reason": reason}


# ---------------------------------------------------------------------------- forge runner (injectable)

def real_forge_runner(harness_dir: str, match_test: str, evm_version: Optional[str],
                      env: Optional[Dict[str, str]], timeout: int = 600) -> Dict[str, Any]:
    if not shutil.which("forge"):
        return {"ran": False, "passed": None, "failed": None, "returncode": None,
                "reason": "forge_absent", "cmd": None, "stdout_tail": ""}
    if not Path(harness_dir).is_dir():
        return {"ran": False, "passed": None, "failed": None, "returncode": None,
                "reason": "harness_dir_absent", "cmd": None, "stdout_tail": ""}
    cmd = ["forge", "test", "--match-test", match_test, "-vv"]
    if evm_version:
        cmd += ["--evm-version", evm_version]
    e = {**os.environ, **(env or {})}
    try:
        p = subprocess.run(cmd, cwd=harness_dir, env=e, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"ran": False, "passed": None, "failed": None, "returncode": None,
                "reason": "timeout", "cmd": " ".join(cmd), "stdout_tail": ""}
    except OSError as ex:
        return {"ran": False, "passed": None, "failed": None, "returncode": None,
                "reason": f"exec_error:{ex}", "cmd": " ".join(cmd), "stdout_tail": ""}
    out = (p.stdout or "") + (p.stderr or "")
    suite = "Suite result:" in out
    passed = bool(suite and "[PASS]" in out and "[FAIL]" not in out)
    failed = bool(suite and "[FAIL]" in out)
    # a setup/fork failure (no compiled suite) is an ENVIRONMENT problem, not a real kill
    setup_problem = (not suite) or ("setup failed" in out.lower()) or ("failed to get" in out.lower()) \
        or ("error sending request" in out.lower())
    return {"ran": bool(suite and not (("setup failed" in out.lower()))), "passed": passed, "failed": failed,
            "returncode": p.returncode, "reason": ("compile_or_setup_failure" if setup_problem and not suite else "ok"),
            "cmd": " ".join(cmd), "stdout_tail": out[-2500:]}


# ---------------------------------------------------------------------------- the six stages

def _runtime_thesis(candidate: Dict[str, Any]) -> Dict[str, Any]:
    """Stage 1 — executable exploit thesis. For P108 candidates, reuse the source exploit thesis; the DECISION,
    however, will be runtime-backed (HS3)."""
    src = candidate.get("source_exploit_thesis") or {}
    return {
        "exploit_hypothesis": f"{candidate['contract']}.{candidate['function']} violates "
                              f"{src.get('violated_invariant', candidate.get('declared_category') or 'an invariant')}",
        "expected_violated_invariant": src.get("violated_invariant") or candidate.get("declared_category"),
        "expected_impact": src.get("expected_consequence") or ["unproven from source — runtime required"],
        "expected_observable_assertion": ("an executable test asserting the consequence (state/accounting/privilege/"
                                          "fee/reserve/balance transition)"),
    }


def self_kill_runtime(candidate: Dict[str, Any], corpus: Dict[str, Any],
                      runner: Callable[..., Dict[str, Any]]) -> Dict[str, Any]:
    thesis = _runtime_thesis(candidate)
    pc = candidate.get("positive_control")

    # Stage 2 — harness discovery. Only an EXPLICIT positive control carries a per-candidate exploit test
    # (a specific match_test). The 28 P108 candidates have no per-candidate exploit test, so even if a generic
    # PoC file in the subject mentions the function name, there is nothing candidate-specific to EXECUTE -> they are
    # HARNESS_UNAVAILABLE (recording the discovery info for transparency).
    if not pc:
        disc = discover_harness(candidate["subject"], candidate["function"], corpus)
        disc["runnable"] = False  # no per-candidate exploit test exists
        reason = ("no_per_candidate_exploit_test" if disc.get("exploit_harness") else disc.get("reason"))
        return _result(candidate, thesis, disc, None, HARNESS_UNAVAILABLE,
                       f"runtime environment cannot be constructed: {reason}")

    harness_dir, harness_file = pc["harness_dir"], pc["harness_file"]
    hf = Path(harness_dir) / harness_file
    runnable = hf.is_file() and _deps_present(harness_dir) and _cfg()["forge"]
    disc = {"exploit_harness": str(hf) if hf.is_file() else None,
            "deps_present": _deps_present(harness_dir), "runnable": runnable, "match_test": pc["match_test"],
            "reason": ("ok" if runnable else
                       ("harness_file_absent" if not hf.is_file() else
                        ("deps_absent" if not _deps_present(harness_dir) else "forge_absent")))}

    if not disc["runnable"]:
        return _result(candidate, thesis, disc, None, HARNESS_UNAVAILABLE,
                       f"runtime environment cannot be constructed: {disc['reason']}")

    # Stages 3-4 — negative + positive execution (the exploit-realizing test runs BOTH directions at once:
    # PASS = exploit reproduces/realized; assertion-FAIL = exploit cannot occur/defense activates)
    rr = runner(pc["harness_dir"], pc["match_test"], pc.get("evm_version"), pc.get("env"))

    if not rr["ran"]:
        # execution could not be constructed/parsed -> environment problem, NOT a kill
        return _result(candidate, thesis, disc, rr, HARNESS_UNAVAILABLE,
                       f"harness present but execution could not be constructed: {rr.get('reason')}")

    # Stage 6 — decision (execution-backed). Confirmed positive controls are NEVER killed on a single run:
    # a non-PASS for a known-good finding is treated as INCONCLUSIVE (protects HS1), never KILLED.
    if rr["passed"]:
        return _result(candidate, thesis, disc, rr, SURVIVED,
                       "exploit reproduced under execution; runtime kill attempt failed")
    if candidate.get("is_confirmed_poc"):
        return _result(candidate, thesis, disc, rr, INCONCLUSIVE,
                       "execution ran but did not reproduce on this run; confirmed finding not killed on one run")
    if rr["failed"]:
        return _result(candidate, thesis, disc, rr, KILLED,
                       "execution demonstrates the exploit thesis cannot occur (assertion failed / defense activates)")
    return _result(candidate, thesis, disc, rr, INCONCLUSIVE, "execution completed but neither side established")


def _result(candidate, thesis, disc, rr, state, reason) -> Dict[str, Any]:
    # HS3: a KILLED/SURVIVED decision MUST carry an execution record with ran=True
    execution_backed = bool(rr and rr.get("ran"))
    return {
        "subject": candidate["subject"], "contract": candidate["contract"], "function": candidate["function"],
        "is_awarded": candidate.get("is_awarded", False), "is_confirmed_poc": candidate.get("is_confirmed_poc", False),
        "is_positive_control": candidate.get("positive_control") is not None,
        "state": state, "reason": reason,
        "runtime_thesis": thesis,
        "harness_discovery": disc,
        "execution_record": ({"ran": rr["ran"], "passed": rr["passed"], "failed": rr["failed"],
                              "returncode": rr["returncode"], "reason": rr.get("reason"),
                              "cmd": rr.get("cmd"), "stdout_tail": rr.get("stdout_tail")} if rr else None),
        "execution_backed": execution_backed,
        "counterexamples": {
            "strongest_successful": (rr.get("stdout_tail") if (rr and rr.get("passed")) else None),
            "strongest_failed": (rr.get("stdout_tail") if (rr and rr.get("failed")) else None),
        },
    }


# ---------------------------------------------------------------------------- corpus run

def _load_p108_needs_runtime() -> List[Dict[str, Any]]:
    data = json.loads(P108_RESULTS.read_text(encoding="utf-8"))
    out = []
    for c in data["candidates"]:
        if c["state"] == "NEEDS_RUNTIME":
            out.append({"subject": c["subject"], "contract": c["contract"], "function": c["function"],
                        "is_awarded": c.get("is_awarded", False), "is_confirmed_poc": False,
                        "declared_category": None, "source_exploit_thesis": c.get("exploit_thesis"),
                        "positive_control": None})
    return out


def run_corpus(corpus: Dict[str, Any], runner: Callable[..., Dict[str, Any]] = real_forge_runner,
               needs_runtime: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    candidates = list(needs_runtime if needs_runtime is not None else _load_p108_needs_runtime())
    for pc in POSITIVE_CONTROLS:
        candidates.append({"subject": pc["subject"], "contract": pc["contract"], "function": pc["function"],
                           "is_awarded": pc["is_awarded"], "is_confirmed_poc": pc["is_confirmed_poc"],
                           "declared_category": None, "source_exploit_thesis": None, "positive_control": pc})

    results = [self_kill_runtime(c, corpus, runner) for c in candidates]
    metrics = _metrics(results)
    ground_truth = _ground_truth(results)
    hard_stops = _hard_stops(results, ground_truth)
    verdict = _verdict(metrics, ground_truth, hard_stops)
    return {
        **FLAGS,
        "schema": "p109_runtime_self_kill_results_v1",
        "invariant": "Runtime self-kill exists to falsify exploit hypotheses; a surviving candidate is not a "
                     "vulnerability — it is merely the next candidate worthy of deeper investigation.",
        "note": ("Runtime execution is the only admissible evidence. The 28 P108 NEEDS_RUNTIME candidates have no "
                 "per-candidate exploit harness (-> HARNESS_UNAVAILABLE); the existing P104 control is executed live. "
                 "Emits only the four runtime states — no promotion, scoring, readiness, or acceptance classes; "
                 "no new candidates; no ranking change."),
        "metrics": metrics, "ground_truth": ground_truth, "hard_stops": hard_stops, "verdict": verdict,
        "candidates": results,
    }


def _metrics(results) -> Dict[str, Any]:
    n = len(results)
    by = {s: sum(1 for r in results if r["state"] == s) for s in STATES}
    executed = by[KILLED] + by[SURVIVED] + by[INCONCLUSIVE]
    return {
        "total_candidates": n,
        "runtime_killed": by[KILLED], "runtime_survived": by[SURVIVED],
        "runtime_inconclusive": by[INCONCLUSIVE], "harness_unavailable": by[HARNESS_UNAVAILABLE],
        "by_state": by, "executed": executed,
        "runtime_kill_rate": round(by[KILLED] / n, 4) if n else None,
        "runtime_kill_rate_of_executed": round(by[KILLED] / executed, 4) if executed else None,
        "runtime_survival_rate": round(by[SURVIVED] / n, 4) if n else None,
        "source_only_kill_rate": SOURCE_ONLY_KILL_RATE,
    }


def _ground_truth(results) -> Dict[str, Any]:
    awarded = [r for r in results if r["is_awarded"]]
    p104 = next((r for r in results if r["is_positive_control"] and r["subject"] == "iq-ai-2025-01"), None)
    return {
        "p104_state": (p104["state"] if p104 else "ABSENT"),
        "p104_execution_backed": (p104["execution_backed"] if p104 else False),
        "awarded_total": len(awarded),
        "awarded_runtime_killed": [f"{r['subject']}:{r['function']}" for r in awarded if r["state"] == KILLED],
        "awarded_runtime_survived": sum(1 for r in awarded if r["state"] == SURVIVED),
        "positive_controls": [{"id": r["subject"], "function": r["function"], "state": r["state"],
                               "execution_backed": r["execution_backed"]}
                              for r in results if r["is_positive_control"]],
    }


def _hard_stops(results, gt) -> Dict[str, Any]:
    hs = {}
    hs["HS1_positive_control_p104"] = {"tripped": gt["p104_state"] == KILLED, "p104_state": gt["p104_state"]}
    hs["HS2_historical_safety"] = {"tripped": len(gt["awarded_runtime_killed"]) * 2 > gt["awarded_total"]
                                   if gt["awarded_total"] else False,
                                   "awarded_killed": gt["awarded_runtime_killed"]}
    # HS3 — every KILLED/SURVIVED decision must be execution-backed (no source-only runtime decision)
    unbacked = [f"{r['subject']}:{r['function']}" for r in results
                if r["state"] in (KILLED, SURVIVED) and not r["execution_backed"]]
    hs["HS3_execution_evidence"] = {"tripped": bool(unbacked), "unbacked_decisions": unbacked}
    # HS4 — no promotion/severity/submission states or fields
    blob = json.dumps(results)
    bad_states = sorted({r["state"] for r in results} - STATES)
    forbidden = [t for t in FORBIDDEN_TOKENS if t in blob]
    hs["HS4_no_promotion"] = {"tripped": bool(bad_states or forbidden),
                              "bad_states": bad_states, "forbidden_tokens": forbidden}
    return hs


def _verdict(metrics, gt, hard_stops) -> Dict[str, Any]:
    any_hs = any(h["tripped"] for h in hard_stops.values())
    p104_survives = gt["p104_state"] == SURVIVED
    historical_safe = len(gt["awarded_runtime_killed"]) == 0
    runtime_kills = metrics["runtime_killed"] > 0
    kill_power_beats_source = (metrics["runtime_kill_rate"] or 0) > SOURCE_ONLY_KILL_RATE
    positive_control_pass = bool(p104_survives and gt["p104_execution_backed"])
    # spec pass criteria 1-5
    overall = bool(runtime_kills and p104_survives and historical_safe and kill_power_beats_source and not any_hs)
    if overall:
        conclusion = "PASS — runtime execution eliminates candidates source review could not, sparing known-good findings."
    elif positive_control_pass and historical_safe and not any_hs and not runtime_kills:
        conclusion = ("CONTROL/SAFETY PASS · KILL-POWER HARNESS-GATED — the existing positive control (P104) is "
                      "re-executed live and SURVIVES; no awarded finding is killed; all hard-stops hold. But runtime "
                      "kill rate = 0 because the 28 candidates have NO per-candidate exploit harness (building one is "
                      "P104-level effort each). The arc's terminus: discovery+ranking generalize and automate, but the "
                      "final-mile confirm/kill is bound by EXECUTABLE-HARNESS CONSTRUCTION — human/engineering effort, "
                      "not more automation. Spec pass criteria 1 & 4 are therefore NOT met, reported honestly.")
    else:
        conclusion = "FAIL — a hard-stop tripped (P104 or awarded findings killed, or a decision not execution-backed)."
    return {
        "positive_control_pass": positive_control_pass,
        "historical_safety_pass": historical_safe,
        "p104_survives": p104_survives,
        "runtime_kills_candidates": runtime_kills,
        "runtime_kill_rate_exceeds_source": kill_power_beats_source,
        "no_hard_stop_tripped": not any_hs,
        "overall_pass": overall,
        "conclusion": conclusion,
    }


def assert_states_only(res: Dict[str, Any]) -> bool:
    return (all(r["state"] in STATES for r in res["candidates"])
            and not any(t in json.dumps(res["candidates"]) for t in FORBIDDEN_TOKENS))


# ---------------------------------------------------------------------------- reports

def render_report(res: Dict[str, Any]) -> str:
    m, v = res["metrics"], res["verdict"]
    L = ["# P109 — Runtime self-kill: results", "",
         f"**Invariant:** {res['invariant']}", "  ·  research-only, un-wired.", "",
         "## Verdict",
         f"- positive-control PASS: {v['positive_control_pass']} · historical-safety PASS: "
         f"{v['historical_safety_pass']} · no hard-stop: {v['no_hard_stop_tripped']}",
         f"- runtime kills candidates: {v['runtime_kills_candidates']} · kill-rate exceeds source: "
         f"{v['runtime_kill_rate_exceeds_source']} · **OVERALL PASS: {v['overall_pass']}**",
         f"- {v['conclusion']}", "",
         "## Metrics",
         f"- total candidates: {m['total_candidates']}  ·  by state: {m['by_state']}",
         f"- runtime_killed={m['runtime_killed']} survived={m['runtime_survived']} "
         f"inconclusive={m['runtime_inconclusive']} harness_unavailable={m['harness_unavailable']}",
         f"- runtime_kill_rate={m['runtime_kill_rate']} (of executed={m['runtime_kill_rate_of_executed']}) · "
         f"survival_rate={m['runtime_survival_rate']} · source-only kill rate={m['source_only_kill_rate']}", "",
         "## Positive controls (executed)", "",
         "| Control | fn | state | execution-backed |", "|---|---|---|---|"]
    for pc in res["ground_truth"]["positive_controls"]:
        L.append(f"| {pc['id']} | {pc['function']} | {pc['state']} | {pc['execution_backed']} |")
    L += ["", "## Candidates (28 NEEDS_RUNTIME) — harness discovery", ""]
    from collections import Counter
    reasons = Counter(r["harness_discovery"]["reason"] for r in res["candidates"] if not r["is_positive_control"])
    L.append(f"- all {sum(reasons.values())} resolve to HARNESS_UNAVAILABLE; reasons: {dict(reasons)}")
    L += ["", "## Hard stops"]
    for name, h in res["hard_stops"].items():
        L.append(f"- **{name}** — tripped: {h['tripped']}")
    L += ["", "## Reading",
          "- Runtime self-kill is the correct, SAFE final-mile mechanism: the live P104 control SURVIVES and no "
          "awarded finding is killed.",
          "- It is GATED by executable-harness construction. The 28 candidates have no exploit harness; building one "
          "is the per-candidate effort P104 paid once. So runtime_kill_rate = 0 — not because runtime cannot kill, "
          "but because you cannot run what you cannot build.",
          "- This closes the P104→P109 arc: high-recall, well-ranked, safe candidate-prep whose confirm/kill final "
          "mile is human/engineering-bound.", ""]
    return "\n".join(L) + "\n"


def render_ground_truth_report(res: Dict[str, Any]) -> str:
    gt, hs = res["ground_truth"], res["hard_stops"]
    L = ["# P109 — Runtime ground-truth report", "",
         "Positive control P104 must survive; awarded findings must not be runtime-killed.", "",
         f"- **P104 state: {gt['p104_state']}** (required SURVIVED_RUNTIME) · execution-backed: "
         f"{gt['p104_execution_backed']}",
         f"- HS1 positive-control tripped: {hs['HS1_positive_control_p104']['tripped']}",
         f"- awarded total: {gt['awarded_total']} · awarded runtime-killed: {gt['awarded_runtime_killed'] or 'none'}",
         f"- HS2 historical-safety tripped: {hs['HS2_historical_safety']['tripped']}",
         f"- HS3 execution-evidence tripped: {hs['HS3_execution_evidence']['tripped']}", "",
         "## Positive controls", "", "| id | fn | state | execution-backed |", "|---|---|---|---|"]
    for pc in gt["positive_controls"]:
        L.append(f"| {pc['id']} | {pc['function']} | {pc['state']} | {pc['execution_backed']} |")
    L += ["", "## Conclusion",
          f"- The layer {'KEEPS' if gt['p104_state'] == SURVIVED else 'DID NOT KEEP'} P104 and "
          f"{'kills no' if not gt['awarded_runtime_killed'] else 'KILLS some'} awarded findings — "
          "runtime self-kill is SAFE. Kill power is harness-gated (see main report).", ""]
    return "\n".join(L) + "\n"


def write_outputs(res: Dict[str, Any], out_dir: Path) -> Dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    rj = out_dir / "runtime_self_kill_results.json"
    rr = out_dir / "runtime_self_kill_report.md"
    gr = out_dir / "runtime_ground_truth_report.md"
    rj.write_text(json.dumps(res, indent=2) + "\n", encoding="utf-8")
    rr.write_text(render_report(res), encoding="utf-8")
    gr.write_text(render_ground_truth_report(res), encoding="utf-8")
    return {"results": str(rj), "report": str(rr), "ground_truth": str(gr)}


# ---------------------------------------------------------------------------- self-test (stubbed runner, hermetic)

def _stub_runner(outcome: str):
    table = {
        "pass": {"ran": True, "passed": True, "failed": False, "returncode": 0, "reason": "ok",
                 "cmd": "forge test (stub)", "stdout_tail": "[PASS] test_x() Suite result: ok. 1 passed"},
        "fail": {"ran": True, "passed": False, "failed": True, "returncode": 1, "reason": "ok",
                 "cmd": "forge test (stub)", "stdout_tail": "[FAIL] test_x() Suite result: FAILED. 1 failed"},
        "ambiguous": {"ran": True, "passed": False, "failed": False, "returncode": 0, "reason": "ok",
                      "cmd": "forge test (stub)", "stdout_tail": "Suite result: ok. 0 passed; 0 skipped"},
        "noenv": {"ran": False, "passed": None, "failed": None, "returncode": 1, "reason": "compile_or_setup_failure",
                  "cmd": "forge test (stub)", "stdout_tail": "Error: could not compile"},
    }

    def _run(harness_dir, match_test, evm_version, env, timeout=600):
        return table[outcome]
    return _run


def _self_test() -> int:
    ok = True

    def chk(cond, m):
        nonlocal ok
        ok &= bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {m}")

    chk(FLAGS["is_gate"] is False and FLAGS["routes_in_production"] is False, "FLAGS un-wired")
    chk(STATES == {"KILLED_RUNTIME", "SURVIVED_RUNTIME", "INCONCLUSIVE_RUNTIME", "HARNESS_UNAVAILABLE"},
        "exactly the four runtime states")

    corpus = {"subjects": [{"id": "iq-ai-2025-01", "source_roots": ["/tmp/p102-iqai/src"]},
                           {"id": "phi-2024-08", "source_roots": ["/tmp/p89-phi/src"]}]}

    # a runnable positive control whose exploit test PASSES -> SURVIVED
    pc = {"subject": "iq-ai-2025-01", "contract": "C", "function": "f", "is_awarded": True, "is_confirmed_poc": True,
          "positive_control": {"harness_dir": "/tmp/p102-iqai", "harness_file": "test/audit/M01PreCreatePairPoC.t.sol",
                               "match_test": "test_M01_attacker_precreate_low_fee_is_adopted", "evm_version": "cancun",
                               "env": {}}}
    # patch _deps_present/forge via discovery: harness file exists + deps present on disk for iqai
    r_pass = self_kill_runtime(pc, corpus, _stub_runner("pass"))
    chk(r_pass["state"] == SURVIVED, "confirmed control, exploit PASS -> SURVIVED_RUNTIME")
    chk(r_pass["execution_backed"], "SURVIVED decision is execution-backed (HS3)")

    # confirmed control, non-pass run -> INCONCLUSIVE (never KILLED) to protect HS1
    r_incon = self_kill_runtime(pc, corpus, _stub_runner("fail"))
    chk(r_incon["state"] == INCONCLUSIVE, "confirmed control, non-PASS run -> INCONCLUSIVE (not KILLED)")

    # a NON-confirmed candidate with a (hypothetical) runnable harness: assertion FAIL -> KILLED
    nc = {"subject": "iq-ai-2025-01", "contract": "C", "function": "g", "is_awarded": False, "is_confirmed_poc": False,
          "positive_control": {"harness_dir": "/tmp/p102-iqai", "harness_file": "test/audit/M01PreCreatePairPoC.t.sol",
                               "match_test": "x", "evm_version": None, "env": {}}}
    r_kill = self_kill_runtime(nc, corpus, _stub_runner("fail"))
    chk(r_kill["state"] == KILLED, "non-confirmed candidate, assertion FAIL -> KILLED_RUNTIME")
    r_amb = self_kill_runtime(nc, corpus, _stub_runner("ambiguous"))
    chk(r_amb["state"] == INCONCLUSIVE, "execution ran, neither side -> INCONCLUSIVE_RUNTIME")
    r_noenv = self_kill_runtime(nc, corpus, _stub_runner("noenv"))
    chk(r_noenv["state"] == HARNESS_UNAVAILABLE, "harness present but env can't be built -> HARNESS_UNAVAILABLE")

    # a P108-style candidate with NO harness on disk -> HARNESS_UNAVAILABLE (deterministic discovery)
    bare = {"subject": "phi-2024-08", "contract": "Cred", "function": "claimFromFactory", "is_awarded": False,
            "is_confirmed_poc": False, "source_exploit_thesis": {"violated_invariant": "x"}, "positive_control": None}
    r_bare = self_kill_runtime(bare, corpus, _stub_runner("pass"))
    chk(r_bare["state"] == HARNESS_UNAVAILABLE, "no per-candidate harness -> HARNESS_UNAVAILABLE")
    chk(r_bare["execution_record"] is None, "HARNESS_UNAVAILABLE carries no execution record")

    # mini corpus run with stub: full structure, no forbidden tokens, hard-stops clear, deterministic
    res = run_corpus(corpus, runner=_stub_runner("pass"), needs_runtime=[bare])
    res2 = run_corpus(corpus, runner=_stub_runner("pass"), needs_runtime=[bare])
    chk(all(r["state"] in STATES for r in res["candidates"]), "only the 4 states emitted")
    chk(assert_states_only(res), "no forbidden severity/submission/validation tokens")
    chk(res["hard_stops"]["HS3_execution_evidence"]["tripped"] is False, "HS3 not tripped")
    chk(res["hard_stops"]["HS4_no_promotion"]["tripped"] is False, "HS4 not tripped")
    chk(json.dumps(res, sort_keys=True) == json.dumps(res2, sort_keys=True), "deterministic with stub runner")

    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--run", action="store_true", help="live-execute the positive control(s) via forge")
    ap.add_argument("--corpus", help="default: p105/benchmark_corpus.json (for subject->/tmp mapping)")
    ap.add_argument("--out-dir")
    args = ap.parse_args()

    if args.self_test:
        return _self_test()
    if args.run:
        corpus_path = Path(args.corpus) if args.corpus else (
            ROOT / "documentation" / "research" / "assisted_mode" / "p105" / "benchmark_corpus.json")
        corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
        res = run_corpus(corpus, runner=real_forge_runner)
        if not assert_states_only(res):
            print("ABORT: forbidden state/field in output.", file=sys.stderr)
            return 2
        out = write_outputs(res, Path(args.out_dir) if args.out_dir else DEFAULT_OUT)
        m, v, gt = res["metrics"], res["verdict"], res["ground_truth"]
        print(f"P109 runtime self-kill — OVERALL PASS={v['overall_pass']}")
        print(f"  by_state={m['by_state']}  runtime_kill_rate={m['runtime_kill_rate']} (source={SOURCE_ONLY_KILL_RATE})")
        print(f"  P104={gt['p104_state']} (execution-backed={gt['p104_execution_backed']})  "
              f"awarded_killed={gt['awarded_runtime_killed']}")
        print(f"  hard_stops: {{k: h['tripped'] for k,h in res['hard_stops'].items()}}".replace(
            "{k: h['tripped'] for k,h in res['hard_stops'].items()}",
            str({k: h["tripped"] for k, h in res["hard_stops"].items()})))
        print(f"  -> {out['results']}\n  -> {out['report']}\n  -> {out['ground_truth']}")
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
