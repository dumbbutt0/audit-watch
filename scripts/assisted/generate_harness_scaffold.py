#!/usr/bin/env python3
"""P110 — Harness scaffold generation (research-only, UN-WIRED).
"Scaffold generation prepares execution; it never proves exploitation and never upgrades candidate status."

Consumes the P110 feasibility assessment and emits an INERT Foundry test skeleton per candidate: a SCAFFOLD banner,
actor declarations, contract handle declarations, a setUp() whose body is TODO comments (fork/deploy/init/fund/config),
and a single test stub whose body is a TODO plus `vm.skip(true)` — so the scaffold is NON-EXECUTABLE and contains NO
exploit logic, NO attack sequence, NO pass/fail or profit assertion, NO runtime conclusion.

`assert_scaffold_is_inert` is the hard-stop guard: it rejects any scaffold containing exploit/consequence tokens or
promotion/severity/submission language. It is used both at generation time and in the tests.

Usage:
    python scripts/assisted/generate_harness_scaffold.py --self-test
    python scripts/assisted/generate_harness_scaffold.py --run
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "assisted"))
import harness_feasibility as FEAS  # noqa: E402  (read-only: assess / run_corpus)

FLAGS = {
    "is_gate": False,
    "research_only": True,
    "review_only": True,
    "routes_in_production": False,
    "routed_manifest_ids": [],
}

DEFAULT_OUT = ROOT / "documentation" / "research" / "assisted_mode" / "p110"

BANNER = ("// SCAFFOLD ONLY — P110 harness preparation. This prepares a runtime environment; it does NOT implement "
          "an\n// adversarial sequence, does NOT establish a finding, assigns no rating, and does not advance "
          "candidate status.\n// The test body is inert (vm.skip). Fill the TODOs to build a runtime check.")

# tokens that must NOT appear in scaffold CODE (exploit logic / consequence assertions / promotion language).
# Checked against comment-stripped code only — safety prose in comments may legitimately negate these words.
_FORBIDDEN = (
    ".call(", ".delegatecall(", "selfdestruct", "assertEq(", "assertGt(", "assertLt(", "assertTrue(", "assertApprox",
    "exploit", "profit", "drain", "stolen", "severity", "submission", "report_ready", "submission_ready",
    "poc_ready", "validated",
)
# value moves executed in a scaffold body would be attack/setup logic — the body must stay inert
_ATTACK_HINT = re.compile(r"(transfer|swap|borrow|mint|burn)\s*\(", re.IGNORECASE)


def _code_only(text: str) -> str:
    return "\n".join(line.split("//", 1)[0] for line in text.splitlines())


@lru_cache(maxsize=1)
def _cfg() -> Dict[str, Any]:
    return {"banner": BANNER}


def assert_scaffold_is_inert(text: str) -> bool:
    """True iff the scaffold is a pure skeleton: has the banner + the inert guard + a TODO, and contains none of the
    forbidden exploit/consequence/promotion tokens or attack-call patterns."""
    low = text.lower()
    if "scaffold only" not in low:
        return False
    if "vm.skip(true)" not in low:
        return False
    if "todo" not in low:
        return False
    code = _code_only(text).lower()
    if any(tok.lower() in code for tok in _FORBIDDEN):
        return False
    if _ATTACK_HINT.search(code):
        return False
    return True


def _actor_decls(actors: List[Dict[str, str]]) -> List[str]:
    seen, out = set(), []
    for a in actors:
        role = a["role"]
        if role in seen:
            continue
        seen.add(role)
        out.append(f'    address {role} = makeAddr("{role}"); // {a["evidence"]}')
    return out


def _handle_decls(deploy_seq: List[str]) -> List[str]:
    return [f"    {c} {c[0].lower() + c[1:]}; // TODO: deploy in setUp" for c in deploy_seq] or \
           ["    // TODO: declare the in-scope contract handle(s) under test"]


def generate_scaffold(assessment: Dict[str, Any]) -> str:
    contract = assessment["contract"]
    function = assessment["function"]
    cls = assessment["classification"]
    dep = assessment.get("dependency_map", {})
    env = assessment.get("environment", {})
    actors = assessment.get("actor_model", [])
    test_name = re.sub(r"\W", "", f"{contract}_{function}")

    L = ["// SPDX-License-Identifier: MIT", _cfg()["banner"], "pragma solidity ^0.8.0;", "",
         '// import "forge-std/Test.sol";  // (uncomment in a Foundry project)',
         f"//   candidate: {assessment['subject']} :: {contract}.{function}",
         f"//   harness classification: {cls} — {assessment.get('rationale','')}"]
    for imp in dep.get("in_scope_imports", [])[:12]:
        L.append(f'// TODO dep (in-scope): import "{imp}";')
    for ext in dep.get("external_integrations", [])[:8]:
        L.append(f'// TODO dep (EXTERNAL — fork): {ext}')
    for tok in dep.get("tokens", [])[:4]:
        L.append(f'// TODO dep (token): {tok}')
    L += ["", f"contract {test_name}HarnessScaffold /* is Test */ {{", "",
          "    // --- actors (who the runtime test needs) ---"]
    L += _actor_decls(actors)
    L += ["", "    // --- contract handles under test ---"]
    L += _handle_decls(env.get("deployment_sequence", []))
    L += ["", "    function setUp() public {"]
    if env.get("fork_required"):
        L.append("        // TODO[fork]: vm.createSelectFork(<RPC>, <block>); reasons: "
                 + "; ".join(env.get("fork_reasons", [])))
    for c in env.get("deployment_sequence", []):
        L.append(f"        // TODO[deploy]: {c[0].lower() + c[1:]} = new {c}(/* constructor args */);")
    if not env.get("deployment_sequence"):
        L.append("        // TODO[deploy]: deploy the in-scope contract(s) under test")
    if env.get("config_required"):
        L.append("        // TODO[config]: call initialize(...) / setter(s) to reach a valid pre-state")
    if env.get("funding_required"):
        L.append("        // TODO[fund]: mint/deal tokens to the actors that need balances")
    L += ["    }", "",
          "    function test_runtime_candidate() public {",
          f"        // TODO: build the runtime check for the candidate invariant on {contract}.{function}.",
          "        // SCAFFOLD ONLY — do NOT implement an adversarial sequence or a consequence check here.",
          "        // A human completes this to either reproduce or refute the behavior at runtime.",
          "        vm.skip(true); // inert: scaffold is not an executable adversarial sequence",
          "    }", "}", ""]
    return "\n".join(L)


# ---------------------------------------------------------------------------- positive-control overlap

def _harness_actors_and_deps(harness_path: str) -> Dict[str, Any]:
    """Read a REAL harness (read-only) and extract its actor names + deployed/imported contract types + fork usage —
    NOT its exploit logic. Used only to score scaffold plausibility."""
    p = Path(harness_path)
    if not p.is_file():
        return {"actors": [], "deployed": [], "fork": False, "present": False}
    text = p.read_text(encoding="utf-8")
    actors = sorted(set(re.findall(r'makeAddr\(\s*"([^"]+)"', text))
                    | set(re.findall(r'address\s+(\w+)\s*=\s*(?:address\(0x|0x)', text)))
    deployed = sorted(set(re.findall(r"\bnew\s+([A-Z]\w+)\s*\(", text)))
    fork = "createSelectFork" in text or "createFork" in text
    return {"actors": actors, "deployed": deployed, "fork": fork, "present": True}


def _control_overlap(control_assessment: Dict[str, Any], harness_path: str) -> Dict[str, Any]:
    real = _harness_actors_and_deps(harness_path)
    scaffold = generate_scaffold(control_assessment)
    env = control_assessment.get("environment", {})
    # fork agreement
    fork_match = (env.get("fork_required") == real["fork"]) if real["present"] else None
    # dependency overlap: do the real harness's deployed types appear in our dep/deploy plan?
    plan_deploys = set(control_assessment.get("dependency_map", {}).get("in_scope_deployable", []))
    plan_all = plan_deploys | set(control_assessment.get("dependency_map", {}).get("interfaces_referenced", []))
    dep_hits = [d for d in real["deployed"] if d in plan_all or any(d in s for s in plan_all)]
    return {
        "harness_present": real["present"],
        "real_fork": real["fork"], "scaffold_fork": env.get("fork_required"), "fork_match": fork_match,
        "real_deployed": real["deployed"], "scaffold_dep_hits": sorted(set(dep_hits)),
        "dep_overlap": (round(len(dep_hits) / len(real["deployed"]), 3) if real["deployed"] else None),
        "real_actor_count": len(real["actors"]), "scaffold_actor_count": len(control_assessment.get("actor_model", [])),
        "scaffold_is_inert": assert_scaffold_is_inert(scaffold),
    }


# ---------------------------------------------------------------------------- run

def run(feasibility: Dict[str, Any]) -> Dict[str, Any]:
    scaffolds = []
    for a in feasibility["assessments"]:
        s = generate_scaffold(a)
        scaffolds.append({"subject": a["subject"], "contract": a["contract"], "function": a["function"],
                          "classification": a["classification"], "scaffold": s,
                          "inert": assert_scaffold_is_inert(s)})
    control_eval = []
    for a in feasibility["controls"]:
        hp = next((c["real_harness"] for c in FEAS.CONTROLS
                   if c["subject"] == a["subject"] and c["function"] == a["function"]), None)
        s = generate_scaffold(a)
        control_eval.append({"subject": a["subject"], "function": a["function"], "classification": a["classification"],
                             "scaffold": s, "inert": assert_scaffold_is_inert(s),
                             "overlap": _control_overlap(a, hp) if hp else None})
    all_inert = all(x["inert"] for x in scaffolds) and all(x["inert"] for x in control_eval)
    return {
        **FLAGS,
        "schema": "p110_harness_scaffold_v1",
        "invariant": feasibility["invariant"],
        "all_scaffolds_inert": all_inert,
        "scaffolds": scaffolds,
        "control_evaluation": control_eval,
    }


def write_outputs(feas: Dict[str, Any], gen: Dict[str, Any], out_dir: Path) -> Dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    scaff_dir = out_dir / "scaffolds"
    scaff_dir.mkdir(exist_ok=True)
    for s in gen["scaffolds"]:
        (scaff_dir / f"{s['subject']}__{s['contract']}_{s['function']}.t.sol").write_text(s["scaffold"], encoding="utf-8")
    for c in gen["control_evaluation"]:
        (scaff_dir / f"CONTROL__{c['subject']}_{c['function']}.t.sol").write_text(c["scaffold"], encoding="utf-8")

    (out_dir / "harness_metrics.json").write_text(json.dumps({
        **feas["metrics"], "all_scaffolds_inert": gen["all_scaffolds_inert"],
        "control_overlap": [{"subject": c["subject"], "function": c["function"],
                             "classification": c["classification"], "overlap": c["overlap"]}
                            for c in gen["control_evaluation"]],
    }, indent=2) + "\n", encoding="utf-8")

    _write_feasibility_md(feas, out_dir / "harness_feasibility_report.md")
    _write_examples_md(feas, gen, out_dir / "harness_scaffold_examples.md")
    return {"metrics": str(out_dir / "harness_metrics.json"),
            "feasibility": str(out_dir / "harness_feasibility_report.md"),
            "examples": str(out_dir / "harness_scaffold_examples.md"),
            "scaffolds_dir": str(scaff_dir)}


def _write_feasibility_md(feas, path: Path):
    m = feas["metrics"]
    L = ["# P110 — Harness feasibility report", "",
         f"**Invariant:** {feas['invariant']}  ·  research-only, un-wired.", "",
         "_Answers 'what would it take to execute this candidate?' — never 'does it exploit?'. No candidate status "
         "is advanced; this layer produces no rating, no finding state, and no downstream-readiness state._", "",
         "## Metrics",
         f"- total candidates: {m['total_candidates']} — SIMPLE={m['simple']} MODERATE={m['moderate']} "
         f"COMPLEX={m['complex']} BLOCKED={m['blocked']}",
         f"- average dependencies: {m['average_dependencies']} · average actors: {m['average_actors']} · "
         f"average setup steps: {m['average_setup_steps']}", "",
         "## Positive controls", "", "| control | classification | fork | rationale |", "|---|---|---|---|"]
    for c in feas["controls"]:
        L.append(f"| {c['subject']}:{c['function']} | {c['classification']} | "
                 f"{c['environment'].get('fork_required')} | {c['rationale']} |")
    L += ["", "## Per-candidate", "",
          "| Subject | Contract.fn | class | fork | deps | actors | setup | blockers |",
          "|---|---|---|---|---|---|---|---|"]
    for a in feas["assessments"]:
        env = a.get("environment", {})
        dep = a.get("dependency_map", {})
        L.append(f"| {a['subject']} | {a['contract']}.{a['function']} | {a['classification']} | "
                 f"{env.get('fork_required')} | {len(dep.get('in_scope_deployable', []))} | "
                 f"{len(a.get('actor_model', []))} | {env.get('setup_steps')} | "
                 f"{'; '.join(a.get('blockers', [])) or '-'} |")
    L += ["", "## Reading",
          "- Classification estimates the human effort to build a runtime harness; it does not estimate whether the "
          "candidate is exploitable.",
          "- A ready setUp skeleton + dependency/actor/environment checklist per candidate is the effort-reduction "
          "deliverable (see scaffolds/).", ""]
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


def _write_examples_md(feas, gen, path: Path):
    L = ["# P110 — Harness scaffold examples", "",
         "Inert Foundry skeletons (banner + actors + handles + setUp TODOs + `vm.skip(true)` test stub). "
         "Each passes `assert_scaffold_is_inert` — no exploit logic, no consequence assertion, no conclusion.", ""]
    L += ["## Positive controls", ""]
    for c in gen["control_evaluation"]:
        L += [f"### {c['subject']} :: {c['function']} ({c['classification']})",
              f"overlap vs real harness: {c['overlap']}", "", "```solidity", c["scaffold"], "```", ""]
    # one representative per classification from the 28
    L += ["## One representative per classification", ""]
    shown = set()
    for s in gen["scaffolds"]:
        if s["classification"] in shown:
            continue
        shown.add(s["classification"])
        L += [f"### {s['subject']} :: {s['contract']}.{s['function']} ({s['classification']})", "",
              "```solidity", s["scaffold"], "```", ""]
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------- self-test

def _self_test() -> int:
    ok = True

    def chk(cond, m):
        nonlocal ok
        ok &= bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {m}")

    chk(FLAGS["is_gate"] is False and FLAGS["routes_in_production"] is False, "FLAGS un-wired")

    assessment = {
        "subject": "fx", "contract": "Vault", "function": "withdraw", "classification": "HARNESS_MODERATE",
        "rationale": "multi-contract", "dependency_map": {"in_scope_imports": ["./Token.sol"],
                                                          "in_scope_deployable": ["Token", "Vault"],
                                                          "external_integrations": [], "tokens": ["ERC20"],
                                                          "interfaces_referenced": ["IERC20"]},
        "environment": {"fork_required": False, "fork_reasons": [], "deployment_sequence": ["Token", "Vault"],
                        "config_required": True, "funding_required": True, "setup_steps": 4},
        "actor_model": [{"role": "attacker", "evidence": "EOA"}, {"role": "admin", "evidence": "owner"}],
    }
    s = generate_scaffold(assessment)
    chk("SCAFFOLD ONLY" in s, "scaffold carries the SCAFFOLD ONLY banner")
    chk("vm.skip(true)" in s, "scaffold test body is inert (vm.skip)")
    chk("TODO" in s, "scaffold has TODO markers")
    chk('makeAddr("attacker")' in s and 'makeAddr("admin")' in s, "actor declarations present")
    chk("Vault vault;" in s, "contract handle declaration present")
    chk("TODO[deploy]" in s and "TODO[config]" in s and "TODO[fund]" in s, "ordered setUp TODOs present")
    chk(assert_scaffold_is_inert(s), "generated scaffold is INERT")

    # planted exploit must be rejected
    bad = s.replace("vm.skip(true); // inert: scaffold is not an executable adversarial sequence",
                    "IERC20(t).transfer(attacker, 1e18); assertGt(t.balanceOf(attacker), 0);")
    chk(assert_scaffold_is_inert(bad) is False, "planted exploit/assertion -> NOT inert (hard stop)")
    chk(assert_scaffold_is_inert("// SCAFFOLD ONLY\nvm.skip(true) // TODO\nseverity: high") is False,
        "promotion/severity token -> NOT inert")
    chk(assert_scaffold_is_inert("nothing here") is False, "missing banner/skip/TODO -> NOT inert")

    # end-to-end with a tiny feasibility result
    feas = {"invariant": "x", "assessments": [assessment], "controls": [],
            "metrics": {"total_candidates": 1, "simple": 0, "moderate": 1, "complex": 0, "blocked": 0,
                        "average_dependencies": 3, "average_actors": 2, "average_setup_steps": 4}}
    gen = run(feas)
    gen2 = run(feas)
    chk(gen["all_scaffolds_inert"] is True, "run(): all scaffolds inert")
    chk(json.dumps(gen, sort_keys=True) == json.dumps(gen2, sort_keys=True), "deterministic")

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
        feas = FEAS.run_corpus(Path(args.corpus) if args.corpus else None)
        gen = run(feas)
        if not gen["all_scaffolds_inert"]:
            print("ABORT: a generated scaffold failed the inertness guard (HS).", file=sys.stderr)
            return 2
        out = write_outputs(feas, gen, Path(args.out_dir) if args.out_dir else DEFAULT_OUT)
        print(f"P110 scaffolds — {len(gen['scaffolds'])} candidate + {len(gen['control_evaluation'])} control "
              f"scaffolds; all inert={gen['all_scaffolds_inert']}")
        for c in gen["control_evaluation"]:
            ov = c["overlap"] or {}
            print(f"  control {c['subject']}:{c['function']} ({c['classification']}) "
                  f"fork_match={ov.get('fork_match')} dep_overlap={ov.get('dep_overlap')}")
        for k, v in out.items():
            print(f"  -> {k}: {v}")
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
