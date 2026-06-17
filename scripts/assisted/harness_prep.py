#!/usr/bin/env python3
"""P111 — Per-candidate harness preparation for the assisted runbook (research-only, UN-WIRED).
"Harness preparation prepares execution; it never proves exploitation and never advances candidate status."

The assisted runbook (documentation/research/assisted_mode/runbook.md, Stage C — PoC handoff) reaches a candidate
that needs runtime behaviour (VALIDATED_FOR_POC_HANDOFF / NEEDS_EXECUTION). This is the per-candidate entrypoint the
runbook calls: it reuses the P110 feasibility classifier + scaffold generator (read-only) to hand the human a
harness CLASSIFICATION + dependency/actor/environment checklist + an INERT Foundry scaffold to fill in. It is the
single command that turns "what would it take to execute this?" into a ready setUp skeleton.

It does NOT route into production, does NOT assign severity, does NOT validate, does NOT advance candidate status, and
does NOT mutate the funnel. The harness class is an advisory EFFORT signal only. Every emitted scaffold must pass the
P110 inertness guard or generation aborts.

Usage:
    python scripts/assisted/harness_prep.py --self-test
    python scripts/assisted/harness_prep.py --subject iq-ai-2025-01 --contract LiquidityManager --function moveLiquidity
    python scripts/assisted/harness_prep.py --intake <assisted_candidate_intake.json>
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
import harness_feasibility as FEAS          # noqa: E402  (P110; read-only — assess / corpus roots)
import generate_harness_scaffold as GEN     # noqa: E402  (P110; read-only — generate_scaffold / inertness guard)

FLAGS = {
    "is_gate": False,
    "research_only": True,
    "review_only": True,
    "routes_in_production": False,
    "routed_manifest_ids": [],
}

DEFAULT_CORPUS = ROOT / "documentation" / "research" / "assisted_mode" / "p105" / "benchmark_corpus.json"
ASSISTED_DIR = ROOT / "documentation" / "research" / "assisted_mode"

BOUNDARY = ("Harness preparation prepares execution; it does NOT prove exploitation and does NOT advance candidate "
            "status. The classification is an advisory EFFORT estimate, not a gate. BLOCKED means runtime "
            "infrastructure is unavailable — it is NOT a verdict that the candidate is safe or unsafe.")


@lru_cache(maxsize=1)
def _cfg() -> Dict[str, Any]:
    return {"corpus": str(DEFAULT_CORPUS)}


def _resolve_source_roots(subject: str, explicit_roots: Optional[List[str]], corpus_path: str) -> List[str]:
    if explicit_roots:
        return list(explicit_roots)
    try:
        roots = FEAS._corpus_roots(corpus_path)
    except (OSError, ValueError):
        roots = {}
    return roots.get(subject, [])


def _candidate_id(subject: str, contract: str, function: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]", "_", f"{subject}__{contract}_{function}")


def prepare(subject: str, contract: str, function: str,
            source_roots: Optional[List[str]] = None, corpus_path: Optional[str] = None) -> Dict[str, Any]:
    """Per-candidate harness preparation. Returns the assessment + the inert scaffold (no status/severity field)."""
    corpus_path = corpus_path or _cfg()["corpus"]
    roots = _resolve_source_roots(subject, source_roots, corpus_path)
    assessment = FEAS.assess(subject, contract, function, roots)
    scaffold = GEN.generate_scaffold(assessment)
    inert = GEN.assert_scaffold_is_inert(scaffold)
    if not inert:
        raise RuntimeError(f"harness_prep: generated scaffold for {subject}:{contract}.{function} is NOT inert "
                           "(P110 guard). Aborting — a scaffold must never contain executable adversarial logic.")
    return {
        **FLAGS,
        "schema": "p111_harness_prep_v1",
        "candidate": {"subject": subject, "contract": contract, "function": function},
        "harness_classification": assessment["classification"],   # advisory EFFORT signal only — NOT a status
        "rationale": assessment["rationale"],
        "dependency_map": assessment["dependency_map"],
        "actor_model": assessment["actor_model"],
        "environment": assessment["environment"],
        "required_components": assessment["required_components"],
        "blockers": assessment["blockers"],
        "scaffold": scaffold,
        "scaffold_inert": inert,
        "boundary": BOUNDARY,
    }


def _render_md(prep: Dict[str, Any]) -> str:
    c = prep["candidate"]
    env = prep["environment"]
    dep = prep["dependency_map"]
    L = [f"# Harness prep — {c['subject']} :: {c['contract']}.{c['function']}", "",
         f"**Harness classification (advisory EFFORT estimate): {prep['harness_classification']}**",
         f"_{prep['rationale']}_", "",
         f"> {prep['boundary']}", "",
         "## Runtime prerequisites (checklist)"]
    if env.get("fork_required"):
        L.append(f"- [ ] **Fork** required: {'; '.join(env.get('fork_reasons', []))}")
    else:
        L.append("- [ ] Local deployment is sufficient (no fork)")
    for step in env.get("deployment_sequence", []):
        L.append(f"- [ ] Deploy `{step}`")
    if env.get("config_required"):
        L.append("- [ ] Initialize / configure to a valid pre-state")
    if env.get("funding_required"):
        L.append("- [ ] Fund the actors that need token balances")
    L += ["", "## Actors to set up"]
    for a in prep["actor_model"]:
        L.append(f"- `{a['role']}` — {a['evidence']}")
    L += ["", "## Dependencies",
          f"- in-scope deployables: {dep.get('in_scope_deployable', [])}",
          f"- external integrations (fork): {dep.get('external_integrations', [])}",
          f"- tokens: {dep.get('tokens', [])}"]
    if prep["blockers"]:
        L += ["", "## Blockers", *[f"- {b}" for b in prep["blockers"]]]
    L += ["", "## Next step",
          "Fill the TODOs in the generated scaffold (`*.scaffold.t.sol`) to build the Stage-C runtime fixture, then "
          "let Stage C classify REPRODUCED / PARTIAL_REPRO / NOT_REPRODUCED. The scaffold is inert until you do.", ""]
    return "\n".join(L) + "\n"


def write_bundle(prep: Dict[str, Any], out_dir: Optional[Path] = None) -> Dict[str, str]:
    c = prep["candidate"]
    cid = _candidate_id(c["subject"], c["contract"], c["function"])
    d = (out_dir or (ASSISTED_DIR / cid / "harness_prep"))
    d.mkdir(parents=True, exist_ok=True)
    feas_path = d / "harness_feasibility.json"
    scaffold_path = d / f"{c['contract']}_{c['function']}.scaffold.t.sol"
    md_path = d / "harness_prep.md"
    feas_blob = {k: v for k, v in prep.items() if k != "scaffold"}
    feas_path.write_text(json.dumps(feas_blob, indent=2) + "\n", encoding="utf-8")
    scaffold_path.write_text(prep["scaffold"], encoding="utf-8")
    md_path.write_text(_render_md(prep), encoding="utf-8")
    return {"feasibility": str(feas_path), "scaffold": str(scaffold_path), "summary": str(md_path)}


def _from_intake(intake: Dict[str, Any]) -> Dict[str, Any]:
    """Pull subject/contract/function (+optional source roots) from an assisted_candidate_intake-style dict."""
    subject = intake.get("subject") or intake.get("audit") or "candidate"
    contract = intake.get("contract")
    function = intake.get("function") or intake.get("entrypoint")
    roots = intake.get("source_roots")
    if not roots and intake.get("source_refs"):
        # derive directories from file:line refs
        roots = sorted({str(Path(str(r).split(":")[0]).parent) for r in intake["source_refs"]})
    return {"subject": subject, "contract": contract, "function": function, "source_roots": roots}


# ---------------------------------------------------------------------------- self-test

def _self_test() -> int:
    ok = True

    def chk(cond, m):
        nonlocal ok
        ok &= bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {m}")

    chk(FLAGS["is_gate"] is False and FLAGS["routes_in_production"] is False, "FLAGS un-wired")

    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="p111_"))
    src = tmp / "src"
    src.mkdir()
    (src / "Dep.sol").write_text("pragma solidity ^0.8.0;\ncontract Dep { uint x; }\n")
    (src / "M.sol").write_text("pragma solidity ^0.8.0;\nimport './Dep.sol';\n"
                               "contract M { address owner; function initialize() public {} "
                               "function g() external { require(msg.sender==owner); } }\n")
    (src / "C.sol").write_text("pragma solidity ^0.8.0;\nimport 'dev-fraxswap/x.sol';\n"
                               "contract C { address constant F = 0xE30521fe7f3bEB6Ad556887b50739d6C7CA667E6; "
                               "function h() external {} }\n")
    roots = [str(src)]

    pm = prepare("fx", "M", "g", source_roots=roots)
    chk(pm["harness_classification"] == "HARNESS_MODERATE", "MODERATE candidate classified")
    chk(pm["scaffold_inert"] is True, "scaffold is inert")
    chk("harness_classification" in pm and "candidate_status" not in pm and "severity" not in json.dumps(pm).lower(),
        "no candidate_status / severity field in output")
    pc = prepare("fx", "C", "h", source_roots=roots)
    chk(pc["harness_classification"] == "HARNESS_COMPLEX" and pc["environment"]["fork_required"],
        "COMPLEX fork candidate classified")

    # bundle write
    out = write_bundle(pm, out_dir=tmp / "bundle")
    chk(Path(out["feasibility"]).is_file() and Path(out["scaffold"]).is_file() and Path(out["summary"]).is_file(),
        "bundle writes 3 files")
    chk(GEN.assert_scaffold_is_inert(Path(out["scaffold"]).read_text()), "written scaffold is inert")
    chk("severity" not in Path(out["summary"]).read_text().lower()
        and "submission" not in Path(out["summary"]).read_text().lower(), "summary md has no promotion tokens")

    # determinism (scaffold + classification stable)
    pm2 = prepare("fx", "M", "g", source_roots=roots)
    chk(pm["scaffold"] == pm2["scaffold"] and pm["harness_classification"] == pm2["harness_classification"],
        "deterministic")

    # abort path: a non-inert scaffold must raise (monkeypatch generate_scaffold to emit exploit code)
    orig = GEN.generate_scaffold
    try:
        GEN.generate_scaffold = lambda a: "// SCAFFOLD ONLY\nfunction t() public { x.call(abi.encode(1)); } // TODO"
        raised = False
        try:
            prepare("fx", "M", "g", source_roots=roots)
        except RuntimeError:
            raised = True
        chk(raised, "non-inert scaffold -> abort (RuntimeError)")
    finally:
        GEN.generate_scaffold = orig

    for p in src.glob("*"):
        p.unlink()
    src.rmdir()
    for p in (tmp / "bundle").glob("*"):
        p.unlink()
    (tmp / "bundle").rmdir()
    tmp.rmdir()
    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--subject")
    ap.add_argument("--contract")
    ap.add_argument("--function")
    ap.add_argument("--source-root", action="append", help="explicit source dir (repeatable)")
    ap.add_argument("--intake", help="assisted_candidate_intake JSON")
    ap.add_argument("--corpus")
    ap.add_argument("--out-dir")
    args = ap.parse_args()

    if args.self_test:
        return _self_test()

    if args.intake:
        spec = _from_intake(json.loads(Path(args.intake).read_text(encoding="utf-8")))
        subject, contract, function = spec["subject"], spec["contract"], spec["function"]
        roots = args.source_root or spec.get("source_roots")
    else:
        subject, contract, function, roots = args.subject, args.contract, args.function, args.source_root

    if not (subject and contract and function):
        ap.error("need --subject --contract --function (or --intake with those fields)")

    prep = prepare(subject, contract, function, source_roots=roots,
                   corpus_path=args.corpus or _cfg()["corpus"])
    out = write_bundle(prep, Path(args.out_dir) if args.out_dir else None)
    print(f"harness_prep — {subject}:{contract}.{function} -> {prep['harness_classification']} "
          f"(advisory effort; inert={prep['scaffold_inert']})")
    for k, v in out.items():
        print(f"  -> {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
