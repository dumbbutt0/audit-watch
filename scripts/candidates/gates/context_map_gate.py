"""
Gate 3 — context_map_gate.

For multicall_invariant candidates, collects the surrounding context: isMulticall references, self-delegatecall
sites, external/public callable functions (callable surface), accounting variable references (borrowAToken,
debtToken, balanceOf(address(this)), totalSupply), the final-invariant validation references, and nearby
require/revert/modifier lines. Emits callable_surface + state_mutation_map + a context summary. Read-only.

PASS -> CONTEXT_MAPPED
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import artifacts as A  # noqa: E402
import policy as P  # noqa: E402

_FUNC_RE = re.compile(r"\bfunction\s+([A-Za-z_]\w*)\s*\(")
_VIS = ("public", "external", "internal", "private")


def _sol_files(root: Path) -> List[Path]:
    return sorted(p for p in root.rglob("*.sol") if p.is_file())


def _refs(files: List[Dict[str, Any]], term: str, limit: int = 40) -> List[str]:
    out = []
    needle = term.lower()
    for f in files:
        for i, ln in enumerate(f["lines"]):
            if needle in ln.lower():
                out.append(f"{f['rel']}:{i + 1}")
                if len(out) >= limit:
                    return out
    return out


def _public_functions(files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for f in files:
        lines = f["lines"]
        for i, ln in enumerate(lines):
            m = _FUNC_RE.search(ln)
            if not m:
                continue
            # signature window
            sig = ln
            for j in range(i, min(i + 12, len(lines))):
                sig = "\n".join(lines[i:j + 1])
                if "{" in lines[j] or ";" in lines[j]:
                    break
            vis = next((v for v in _VIS if re.search(r"\b" + v + r"\b", sig)), "internal")
            if vis in ("public", "external"):
                body = "\n".join(lines[i:min(i + 30, len(lines))]).lower()
                out.append({
                    "function": m.group(1), "file": f["rel"], "line": i + 1, "visibility": vis,
                    "mutability": "payable" if re.search(r"\bpayable\b", sig) else
                                  ("view" if re.search(r"\bview\b", sig) else
                                   ("pure" if re.search(r"\bpure\b", sig) else "nonpayable")),
                    "modifiers": sorted({t for t in re.findall(r"\b([A-Za-z_]\w*)\b", sig)
                                         if t in ("whenNotPaused", "nonReentrant", "onlyOwner", "onlyRole",
                                                  "onlyGovernance", "onlyAdmin")}),
                    "_body_lc": body,
                })
    return out


def run(cand: Dict[str, Any], target_root: Optional[str], roots: Optional[List[Path]] = None,
        facade_files: Optional[List[str]] = None) -> Tuple[Dict[str, Any], Dict[str, Any], str]:
    """Returns (callable_surface_body, state_mutation_map_body, state). If facade_files is given, the callable
    surface is restricted to public/external functions defined in those files (the real multicall-callable set);
    otherwise it falls back to all public/external functions under the target root."""
    troot = (A.ROOT / target_root) if target_root else A.ROOT
    req = P.detector_requirements(cand.get("detector", ""))
    terms = req.get("context_map_terms", ["isMulticall", "delegatecall", "balanceOf", "totalSupply"])
    accounting = P.load_policy().get("accounting_terms", [])

    files = [{"rel": str(f.relative_to(A.ROOT)),
              "lines": f.read_text(encoding="utf-8", errors="replace").splitlines()}
             for f in (_sol_files(troot) if troot.is_dir() else [])]

    term_refs = {t: _refs(files, t) for t in terms}
    surface_files = ([f for f in files if f["rel"] in set(facade_files)] if facade_files else files)
    pubs = _public_functions(surface_files)
    fn = cand.get("function")

    # callable surface: public/external functions that are NOT the multicall facade itself, mutating accounting
    callable_subcalls = []
    for p in pubs:
        if p["function"] == fn:
            continue
        mutates = any(a.lower() in p["_body_lc"] for a in accounting)
        validation_sensitive = any(v in p["_body_lc"] for v in ("validate", "require", "cap", "revert"))
        privileged = bool(set(p["modifiers"]) & {"onlyOwner", "onlyRole", "onlyGovernance", "onlyAdmin"})
        callable_subcalls.append({
            "function": p["function"], "file": p["file"], "line": p["line"], "mutability": p["mutability"],
            "callable_in_multicall": (p["mutability"] == "payable") if not privileged else "unknown",
            "blocked_in_multicall": privileged,
            "mutates_accounting": mutates,
            "validation_sensitive": validation_sensitive,
        })

    callable_surface = {
        "candidate_function": cand.get("candidate_surface"),
        "facade_files": facade_files or "all (no facade resolved)",
        "callable_subcalls": callable_subcalls[:80],
        "callable_subcalls_total": len(callable_subcalls),
        "note": "Functions of the discovered facade contract. callable_in_multicall is a heuristic (payable "
                "siblings of the facade); 'unknown' where privileged. Self-delegatecall has no value, so "
                "non-payable siblings may also be reachable — confirm in defense_map gate.",
    }

    # state mutation map
    snippet = cand.get("code_snippet") or ""
    before_after = sorted(set(re.findall(r"\b(\w*(?:Before|After))\b", snippet)))
    state_mutation_map = {
        "isMulticall_refs": term_refs.get("isMulticall", []),
        "self_delegatecall_refs": term_refs.get("functionDelegateCall(address(this)", []) or term_refs.get("delegatecall", []),
        "state_variables": [r for r in term_refs.get("isMulticall", [])][:8],
        "token_balances": term_refs.get("balanceOf(address(this))", []) or term_refs.get("borrowAToken", []),
        "totalsupply_refs": term_refs.get("totalSupply", []),
        "accounting_refs": {"borrowAToken": term_refs.get("borrowAToken", []),
                            "debtToken": term_refs.get("debtToken", [])},
        "final_invariant_refs": term_refs.get("validateBorrowATokenIncreaseLteDebtTokenDecrease", []),
        "mutating_functions": [c["function"] for c in callable_subcalls if c["mutates_accounting"]],
        "reading_functions": sorted({Path(r.split(":")[0]).name for r in
                                     term_refs.get("validateBorrowATokenIncreaseLteDebtTokenDecrease", [])}),
        "before_after_variables": before_after,
        "term_reference_counts": {t: len(v) for t, v in term_refs.items()},
    }
    return callable_surface, state_mutation_map, "CONTEXT_MAPPED"
