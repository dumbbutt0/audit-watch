"""
Gate 2 — reachability_gate.

Determines whether the candidate function can be reached from an external/public entrypoint. For internal library
functions (e.g. Multicall.multicall) it searches for an external/public facade of the same name or callers that
route into the library. Records the call path, access controls, and privileged blockers. Read-only.

PASS  -> REACHABLE (a public/external, non-privileged-only entrypoint reaches it)
NEEDS_CONTEXT -> unresolved (no facade/caller found)
KILLED -> definitively unreachable (private/internal with zero callers)
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import artifacts as A  # noqa: E402
import policy as P  # noqa: E402

_VIS = ("public", "external", "internal", "private")


def _sol_files(target_root: Path) -> List[Path]:
    return sorted(p for p in target_root.rglob("*.sol") if p.is_file())


def _signature_window(lines: List[str], start: int) -> Tuple[str, int]:
    end = start
    for j in range(start, min(start + 30, len(lines))):
        if "{" in lines[j] or ";" in lines[j]:
            end = j
            break
        end = j
    return "\n".join(lines[start:end + 1]), end


def _parse_visibility(sig: str) -> str:
    for v in _VIS:
        if re.search(r"\b" + v + r"\b", sig):
            return v
    return "internal"  # solidity default for functions w/o explicit visibility varies; report internal/unknown


def run(cand: Dict[str, Any], target_root: Optional[str], roots: Optional[List[Path]] = None) -> Tuple[Dict[str, Any], str]:
    fn = cand.get("function")
    cand_file = cand.get("file")
    troot = (A.ROOT / target_root) if target_root else A.ROOT
    priv_terms = P.load_policy().get("privileged_modifier_terms", [])
    files = _sol_files(troot) if troot.is_dir() else []

    entrypoints: List[Dict[str, Any]] = []
    callers: List[str] = []
    fn_pat = re.compile(r"\bfunction\s+" + re.escape(fn or "") + r"\s*\(") if fn else None
    caller_pat = re.compile(r"\b(?:state|self|this)\.\s*" + re.escape(fn or "") + r"\s*\(") if fn else None

    for f in files:
        rel = str(f.relative_to(A.ROOT))
        lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
        for i, ln in enumerate(lines):
            if fn_pat and fn_pat.search(ln):
                sig, _ = _signature_window(lines, i)
                vis = _parse_visibility(sig)
                mods = [m for m in re.findall(r"\b([A-Za-z_]\w*)\b", sig) if m in
                        (priv_terms + ["whenNotPaused", "nonReentrant"])]
                # an external/public definition NOT in the candidate's own (internal) file is a facade
                is_facade = vis in ("public", "external")
                if is_facade:
                    is_interface_decl = (";" in sig and "{" not in sig)
                    entrypoints.append({
                        "function": f"{fn}(...)", "file": rel, "line": i + 1, "visibility": vis,
                        "payable": bool(re.search(r"\bpayable\b", sig)), "modifiers": mods,
                        "is_external_facade": rel != cand_file,
                        "is_interface_decl": is_interface_decl,
                    })
            if caller_pat and caller_pat.search(ln):
                callers.append(f"{rel}:{i + 1}")

    # classify
    non_priv_facades = [e for e in entrypoints if not (set(e["modifiers"]) & set(priv_terms))]
    privileged_blockers = sorted({m for e in entrypoints for m in e["modifiers"] if m in priv_terms})
    access_controls = sorted({m for e in entrypoints for m in e["modifiers"]})

    if non_priv_facades:
        attacker_can_reach: Optional[bool] = True
        verdict = "REACHABLE"
        state = "REACHABLE"
    elif entrypoints and not non_priv_facades:
        attacker_can_reach = False
        verdict = "PRIVILEGED_ONLY"
        state = "NEEDS_CONTEXT"  # privileged-only is not a hard kill at stage 1 — flag for human
    else:
        attacker_can_reach = None
        verdict = "UNRESOLVED"
        state = "NEEDS_CONTEXT"

    # call path
    call_path: List[str] = []
    if non_priv_facades:
        e = non_priv_facades[0]
        call_path = [f"{e['file']}:{e['line']} {fn}(...) [{e['visibility']}"
                     + (" payable" if e["payable"] else "") + "]"]
        if callers:
            call_path.append(f"→ state.{fn}(...) [internal library @ {cand_file}]")
        else:
            call_path.append(f"→ {cand.get('candidate_surface')} [{cand.get('visibility','internal')}]")

    body = {
        "candidate_function": cand.get("candidate_surface"),
        "candidate_visibility": cand.get("visibility"),
        "entrypoints": entrypoints,
        "external_facade_found": any(e.get("is_external_facade") for e in entrypoints),
        "callers": callers,
        "call_path": call_path,
        "access_controls": access_controls,
        "privileged_blockers": privileged_blockers,
        "attacker_can_reach": attacker_can_reach,
        "reachability_verdict": verdict,
        "reason": _reason(verdict, entrypoints, cand),
    }
    return body, state


def _reason(verdict: str, entrypoints: List[Dict[str, Any]], cand: Dict[str, Any]) -> str:
    if verdict == "REACHABLE":
        return f"public/external facade for {cand.get('function')} found; not gated by a privileged-only modifier"
    if verdict == "PRIVILEGED_ONLY":
        return "only privileged (owner/role/governance) entrypoints found — attacker reachability not established"
    return (f"no external/public facade or caller of {cand.get('function')} found under the target root — "
            "reachability unresolved (candidate is internal/library)")
