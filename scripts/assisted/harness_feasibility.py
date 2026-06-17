#!/usr/bin/env python3
"""P110 — Harness feasibility assessment (research-only, UN-WIRED).
"Scaffold generation prepares execution; it never proves exploitation and never upgrades candidate status."

P109 showed runtime self-kill is gated by harness availability (28 HARNESS_UNAVAILABLE). This module answers, per
candidate, *"what runtime infrastructure would it take to execute this?"* — purely from source — by building a
dependency map, an actor model, an environment-requirements profile, and a harness CLASSIFICATION
(SIMPLE / MODERATE / COMPLEX / BLOCKED). It NEVER answers *"does this exploit?"*: no exploit logic, no severity, no
validation, no candidate-status change.

Reuses the frozen source helpers read-only (benchmark_replay._resolve_sol_files). No execution, no network.

Usage:
    python scripts/assisted/harness_feasibility.py --self-test
    python scripts/assisted/harness_feasibility.py --run
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
import benchmark_replay as BENCH  # noqa: E402  (read-only: _resolve_sol_files)

FLAGS = {
    "is_gate": False,
    "research_only": True,
    "review_only": True,
    "routes_in_production": False,
    "routed_manifest_ids": [],
}

P109_RESULTS = ROOT / "documentation" / "research" / "assisted_mode" / "p109" / "runtime_self_kill_results.json"
DEFAULT_CORPUS = ROOT / "documentation" / "research" / "assisted_mode" / "p105" / "benchmark_corpus.json"
DEFAULT_OUT = ROOT / "documentation" / "research" / "assisted_mode" / "p110"

SIMPLE, MODERATE, COMPLEX, BLOCKED = "HARNESS_SIMPLE", "HARNESS_MODERATE", "HARNESS_COMPLEX", "HARNESS_BLOCKED"
CLASSES = {SIMPLE, MODERATE, COMPLEX, BLOCKED}

# positive controls: confirmed findings with a REAL harness on disk (used for overlap evaluation, read-only)
CONTROLS = [
    {"subject": "iq-ai-2025-01", "contract": "LiquidityManager", "function": "moveLiquidity",
     "real_harness": "/tmp/p102-iqai/test/audit/M01PreCreatePairPoC.t.sol"},
    {"subject": "secondswap-2024-12", "contract": "SecondSwap_Marketplace", "function": "spotPurchase",
     "real_harness": "/tmp/p97-secondswap/test/audit/M11SelfPurchasePoC.t.sol"},
]

_LIB_MARKERS = ("openzeppelin", "forge-std", "solmate", "hardhat", "solady")
_EXTERNAL_MARKERS = ("dev-fraxswap", "fraxswap", "uniswap", "chainlink", "aave", "curve", "balancer", "pyth")
_IMPORT_RE = re.compile(r"""import\s+(?:[^"';]*\s+from\s+)?["']([^"']+)["']""")
_ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")
_NEW_RE = re.compile(r"\bnew\s+([A-Z]\w+)\s*\(")
_IFACE_RE = re.compile(r"\bI[A-Z]\w+\b")
_CONTAINER_RE = re.compile(r"\b(?:contract|library|interface|abstract\s+contract)\s+([A-Za-z_]\w*)")


@lru_cache(maxsize=1)
def _cfg() -> Dict[str, Any]:
    return {"complex_contract_threshold": 7, "exclude": list(_default_excludes())}


def _default_excludes():
    return ["/test", "/tests", "/mock", "Mock", "node_modules", "/out/", "/cache/", "forge-std"]


@lru_cache(maxsize=64)
def _corpus_roots(corpus_path: str) -> Dict[str, List[str]]:
    c = json.loads(Path(corpus_path).read_text(encoding="utf-8"))
    return {s["id"]: s.get("source_roots", []) for s in c["subjects"]}


def _subject_root(source_roots: List[str]) -> Optional[Path]:
    if not source_roots:
        return None
    parts = Path(source_roots[0]).parts
    if len(parts) >= 3 and parts[1] == "tmp":
        return Path(parts[0], parts[1], parts[2])
    return Path(source_roots[0])


def _locate_contract_file(source_roots: List[str], contract: str) -> Optional[Path]:
    rx = re.compile(r"\b(?:contract|library|interface|abstract\s+contract)\s+" + re.escape(contract) + r"\b")
    for f in BENCH._resolve_sol_files(source_roots, _cfg()["exclude"]):
        try:
            if rx.search(f.read_text(encoding="utf-8")):
                return f
        except (OSError, UnicodeDecodeError):
            continue
    return None


def _import_exists(target: str, subject_root: Optional[Path]) -> bool:
    if not subject_root or not subject_root.is_dir():
        return True  # cannot verify -> do not flag as blocker
    base = Path(target).name
    return any(subject_root.rglob(base))


def _is_interface_stem(stem: str) -> bool:
    return bool(re.match(r"I[A-Z]", stem)) or "_I" in stem


def _concrete_sibling(stem: str, subject_root: Optional[Path]) -> Optional[str]:
    """Map an interface stem to a concrete sibling contract that EXISTS on disk: IFoo->Foo, X_IY->X_Y."""
    cands = []
    if re.match(r"I[A-Z]", stem):
        cands.append(stem[1:])
    if "_I" in stem:
        cands.append(stem.replace("_I", "_", 1))
    for c in cands:
        if subject_root and subject_root.is_dir() and any(subject_root.rglob(c + ".sol")):
            return c
    return None


def _dependency_map(text: str, contract: str, subject_root: Optional[Path]) -> Dict[str, Any]:
    imports = _IMPORT_RE.findall(text)
    in_scope, libraries, tokens, external = [], [], [], []
    deployable, missing_deployable, missing_interface, resolved_concretes = set(), [], [], []
    for imp in imports:
        low = imp.lower()
        if any(m in low for m in _EXTERNAL_MARKERS):
            external.append(imp)
        elif any(m in low for m in _LIB_MARKERS):
            libraries.append(imp)
        elif imp.startswith(".") or imp.startswith("src/") or imp.startswith("contracts/"):
            in_scope.append(imp)
            stem = Path(imp).stem
            present = _import_exists(imp, subject_root)
            if _is_interface_stem(stem) or "interface" in low:
                if not present:
                    missing_interface.append(imp)
                # resolve the concrete implementation that a harness would deploy
                concrete = _concrete_sibling(stem, subject_root)
                if concrete:
                    deployable.add(concrete); resolved_concretes.append(concrete)
            else:
                deployable.add(stem)
                if not present:
                    missing_deployable.append(imp)
        else:
            libraries.append(imp)
        if "erc20" in low or "erc721" in low or "erc1155" in low:
            tokens.append(imp)
    # the contract under test is itself deployed by the harness
    deployable.add(contract)
    interfaces = sorted(set(_IFACE_RE.findall(text)))
    return {
        "in_scope_imports": sorted(set(in_scope)),
        "in_scope_deployable": sorted(deployable),
        "resolved_concrete_from_interfaces": sorted(set(resolved_concretes)),
        "libraries": sorted(set(libraries)),
        "tokens": sorted(set(tokens)),
        "external_integrations": sorted(set(external)),
        "interfaces_referenced": interfaces[:25],
        "hardcoded_addresses": sorted(set(_ADDR_RE.findall(text))),
        "new_deploys_in_source": sorted(set(_NEW_RE.findall(text))),
        "missing_deployable_imports": sorted(set(missing_deployable)),
        "missing_interface_imports": sorted(set(missing_interface)),
    }


def _actor_model(text: str) -> List[Dict[str, str]]:
    t = text.lower()
    actors = [{"role": "attacker", "evidence": "EOA entrypoint (default adversary)"}]
    if re.search(r"onlyowner|onlyadmin|onlyrole|_checkrole|hasrole|require\(\s*msg\.sender\s*==", t):
        actors.append({"role": "admin", "evidence": "owner/role/privileged guard present"})
    if re.search(r"\bbalance|\bshares|\ballocation|\baccount\b|vesting|stepsclaimed", t):
        actors.append({"role": "victim_user", "evidence": "per-user accounting present"})
    if re.search(r"addliquidity|liquidity|reserve|\blp\b|mint.*pool", t):
        actors.append({"role": "liquidity_provider", "evidence": "liquidity/reserve mechanics present"})
    if re.search(r"factory|\bpair\b|\bpool\b|router|oracle", t):
        actors.append({"role": "protocol", "evidence": "external protocol surface (factory/pair/pool/oracle)"})
    if re.search(r"governor|timelock|governance|proposal|\bvote", t):
        actors.append({"role": "governance", "evidence": "governance/timelock present"})
    return actors


def _environment(dep: Dict[str, Any], text: str) -> Dict[str, Any]:
    t = text.lower()
    fork_reasons = []
    if dep["hardcoded_addresses"]:
        fork_reasons.append(f"{len(dep['hardcoded_addresses'])} hardcoded mainnet address(es)")
    if dep["external_integrations"]:
        fork_reasons.append("external protocol integration import(s): " + ", ".join(dep["external_integrations"][:3]))
    fork_required = bool(fork_reasons)
    config_required = bool(re.search(r"\binitialize\b|function\s+set[A-Z]", text))
    funding_required = bool(dep["tokens"] or re.search(r"transfer|safetransfer|\bmint\b", t))
    deploy_seq = dep["in_scope_deployable"]
    setup_steps = len(deploy_seq) + (1 if fork_required else 0) + (1 if funding_required else 0) \
        + (1 if config_required else 0)
    return {
        "fork_required": fork_required, "fork_reasons": fork_reasons,
        "local_deployable": not fork_required,
        "deployment_sequence": deploy_seq,
        "funding_required": funding_required, "config_required": config_required,
        "setup_steps": setup_steps,
    }


def assess(subject: str, contract: str, function: str, source_roots: List[str],
           is_control: bool = False) -> Dict[str, Any]:
    subject_root = _subject_root(source_roots)
    f = _locate_contract_file(source_roots, contract)
    if f is None:
        return {"subject": subject, "contract": contract, "function": function, "is_control": is_control,
                "classification": BLOCKED, "rationale": "contract source file not found in scope",
                "dependency_map": {}, "actor_model": [], "environment": {}, "required_components": [],
                "blockers": ["contract_source_not_found"]}
    text = f.read_text(encoding="utf-8")
    dep = _dependency_map(text, contract, subject_root)
    actors = _actor_model(text)
    env = _environment(dep, text)

    blockers = []
    if dep["missing_deployable_imports"]:
        blockers.append("missing_deployable_imports: " + ", ".join(dep["missing_deployable_imports"][:3]))

    n_deploy = len(env["deployment_sequence"])
    if blockers:
        classification = BLOCKED
        rationale = "unresolved in-scope DEPLOYABLE dependencies on disk"
    elif env["fork_required"] or n_deploy >= _cfg()["complex_contract_threshold"]:
        classification = COMPLEX
        rationale = ("fork / external-state recreation required (" + "; ".join(env["fork_reasons"]) + ")"
                     if env["fork_required"]
                     else f"large protocol graph ({n_deploy} in-scope contracts to deploy)")
    elif n_deploy >= 2 or env["config_required"]:
        classification = MODERATE
        rationale = f"{n_deploy} in-scope contract(s), local deploy with ordering / initialization"
    else:
        classification = SIMPLE
        rationale = "isolated contract, local deployment sufficient, minimal actors"

    required = []
    required += [f"deploy {c}" for c in env["deployment_sequence"]]
    if env["fork_required"]:
        required.append("fork (external state) — " + "; ".join(env["fork_reasons"]))
    if env["config_required"]:
        required.append("initialize/config")
    if env["funding_required"]:
        required.append("fund actors with tokens")
    required += [f"actor: {a['role']}" for a in actors]

    return {
        "subject": subject, "contract": contract, "function": function, "is_control": is_control,
        "source_file": str(f),
        "classification": classification, "rationale": rationale,
        "dependency_map": dep, "actor_model": actors, "environment": env,
        "required_components": required, "blockers": blockers,
    }


# ---------------------------------------------------------------------------- corpus run

def _load_p109_unavailable() -> List[Dict[str, str]]:
    data = json.loads(P109_RESULTS.read_text(encoding="utf-8"))
    return [{"subject": c["subject"], "contract": c["contract"], "function": c["function"]}
            for c in data["candidates"] if c["state"] == "HARNESS_UNAVAILABLE" and not c["is_positive_control"]]


def run_corpus(corpus_path: Optional[Path] = None,
               candidates: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    corpus_path = str(corpus_path or DEFAULT_CORPUS)
    roots = _corpus_roots(corpus_path)
    cands = candidates if candidates is not None else _load_p109_unavailable()

    assessments = [assess(c["subject"], c["contract"], c["function"], roots.get(c["subject"], []))
                   for c in cands]
    controls = [assess(c["subject"], c["contract"], c["function"], roots.get(c["subject"], []), is_control=True)
                for c in CONTROLS]

    return {
        **FLAGS,
        "schema": "p110_harness_feasibility_v1",
        "invariant": "Scaffold generation prepares execution; it never proves exploitation and never upgrades "
                     "candidate status.",
        "assessments": assessments,
        "controls": controls,
        "metrics": _metrics(assessments),
    }


def _metrics(assessments: List[Dict[str, Any]]) -> Dict[str, Any]:
    n = len(assessments)
    by = {c: sum(1 for a in assessments if a["classification"] == c) for c in CLASSES}

    def _avg(key_fn):
        vals = [key_fn(a) for a in assessments if a.get("environment")]
        return round(sum(vals) / len(vals), 3) if vals else 0.0
    return {
        "total_candidates": n,
        "simple": by[SIMPLE], "moderate": by[MODERATE], "complex": by[COMPLEX], "blocked": by[BLOCKED],
        "average_dependencies": _avg(lambda a: len(a["dependency_map"].get("in_scope_deployable", []))
                                     + len(a["dependency_map"].get("external_integrations", []))
                                     + len(a["dependency_map"].get("tokens", []))),
        "average_actors": _avg(lambda a: len(a["actor_model"])),
        "average_setup_steps": _avg(lambda a: a["environment"].get("setup_steps", 0)),
    }


# ---------------------------------------------------------------------------- self-test

def _write(d: Path, name: str, body: str):
    (d / name).write_text(body, encoding="utf-8")


def _self_test() -> int:
    ok = True

    def chk(cond, m):
        nonlocal ok
        ok &= bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {m}")

    chk(FLAGS["is_gate"] is False and FLAGS["routes_in_production"] is False, "FLAGS un-wired")
    chk(CLASSES == {SIMPLE, MODERATE, COMPLEX, BLOCKED}, "exactly four harness classes")

    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="p110_feas_"))
    src = tmp / "src"
    src.mkdir()
    _write(src, "A.sol", "pragma solidity ^0.8.0;\ncontract A { function f() external pure returns (uint){return 1;} }\n")
    _write(src, "Dep.sol", "pragma solidity ^0.8.0;\ncontract Dep { uint x; }\n")
    _write(src, "Dep2.sol", "pragma solidity ^0.8.0;\ncontract Dep2 { uint y; }\n")
    _write(src, "M.sol", "pragma solidity ^0.8.0;\nimport './Dep.sol';\nimport './Dep2.sol';\n"
                         "contract M { address owner; function initialize() public {} "
                         "function g() external { require(msg.sender==owner); } }\n")
    _write(src, "C.sol", "pragma solidity ^0.8.0;\nimport 'dev-fraxswap/x.sol';\n"
                         "contract C { address constant F = 0xE30521fe7f3bEB6Ad556887b50739d6C7CA667E6; "
                         "function h() external {} }\n")
    _write(src, "B.sol", "pragma solidity ^0.8.0;\nimport './Missing.sol';\ncontract B { function k() external {} }\n")
    roots = [str(src)]

    a = assess("x", "A", "f", roots)
    chk(a["classification"] == SIMPLE, "isolated contract -> SIMPLE")
    m = assess("x", "M", "g", roots)
    chk(m["classification"] == MODERATE, "multi-contract + initialize -> MODERATE")
    c = assess("x", "C", "h", roots)
    chk(c["classification"] == COMPLEX and c["environment"]["fork_required"], "hardcoded addr / external dep -> COMPLEX (fork)")
    b = assess("x", "B", "k", roots)
    chk(b["classification"] == BLOCKED and b["blockers"], "missing in-scope import -> BLOCKED")
    nf = assess("x", "DoesNotExist", "z", roots)
    chk(nf["classification"] == BLOCKED, "contract not found -> BLOCKED")

    chk(any(act["role"] == "admin" for act in m["actor_model"]), "admin actor inferred from msg.sender guard")
    chk("Dep" in m["environment"]["deployment_sequence"], "in-scope deployable contract captured")

    res = run_corpus(candidates=[{"subject": "x", "contract": "A", "function": "f"}],
                     corpus_path=_fake_corpus(tmp, roots))
    chk(res["metrics"]["total_candidates"] == 1, "metrics computed")
    res2 = run_corpus(candidates=[{"subject": "x", "contract": "A", "function": "f"}],
                      corpus_path=_fake_corpus(tmp, roots))
    chk(json.dumps(res["assessments"], sort_keys=True) == json.dumps(res2["assessments"], sort_keys=True),
        "deterministic")

    for p in src.glob("*"):
        p.unlink()
    (tmp / "corpus.json").unlink(missing_ok=True)
    src.rmdir()
    tmp.rmdir()
    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def _fake_corpus(tmp: Path, roots: List[str]) -> Path:
    p = tmp / "corpus.json"
    p.write_text(json.dumps({"subjects": [{"id": "x", "source_roots": roots}]}), encoding="utf-8")
    _corpus_roots.cache_clear()
    return p


def write_outputs(res: Dict[str, Any], out_dir: Path) -> str:
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / "harness_feasibility.json"
    p.write_text(json.dumps(res, indent=2) + "\n", encoding="utf-8")
    return str(p)


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
        res = run_corpus(Path(args.corpus) if args.corpus else None)
        out = write_outputs(res, Path(args.out_dir) if args.out_dir else DEFAULT_OUT)
        m = res["metrics"]
        print(f"P110 harness feasibility — {m['total_candidates']} candidates: "
              f"SIMPLE={m['simple']} MODERATE={m['moderate']} COMPLEX={m['complex']} BLOCKED={m['blocked']}")
        print(f"  avg deps={m['average_dependencies']} actors={m['average_actors']} setup_steps={m['average_setup_steps']}")
        for c in res["controls"]:
            print(f"  control {c['subject']}:{c['function']} -> {c['classification']}")
        print(f"  -> {out}")
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
