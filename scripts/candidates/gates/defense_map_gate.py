"""
Gate 4 — defense_map_gate.

Maps the defenses/checks on the reachable path: entry-facade modifiers, multicall-engine behavior, every
isMulticall-dependent branch (with surrounding code, what is skipped/changed, and a coverage status), accounting
checks, and per callable-surface function. Reuses Stage-1 in-memory results (reachability / callable_surface /
state_mutation_map) and reads source for branch context. Read-only.

PASS -> DEFENSE_MAPPED ; NEEDS_CONTEXT (nothing to map) ; KILLED (not used at this stage — a guard "killing" the
candidate is a sequence/negative-gate conclusion, not a static one).
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import artifacts as A  # noqa: E402
import policy as P  # noqa: E402

_PRIV = ("onlyOwner", "onlyRole", "onlyGovernance", "onlyAdmin", "requiresAuth")


def _lines(rel: str) -> List[str]:
    try:
        return (A.ROOT / rel).read_text(encoding="utf-8", errors="replace").splitlines()
    except (FileNotFoundError, OSError):
        return []


def _surrounding(rel: str, line: int, ctx: int = 4) -> str:
    lines = _lines(rel)
    if not lines:
        return ""
    lo, hi = max(0, line - 1 - ctx), min(len(lines), line - 1 + ctx + 1)
    return "\n".join(lines[lo:hi])


def _grep(target_root: Path, needle: str, limit: int = 10) -> List[str]:
    out = []
    for f in sorted(target_root.rglob("*.sol")):
        for i, ln in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines()):
            if needle in ln:
                out.append(f"{f.relative_to(A.ROOT)}:{i + 1}")
                if len(out) >= limit:
                    return out
    return out


def run(cand: Dict[str, Any], target_root: Optional[str],
        reach_body: Optional[Dict[str, Any]] = None,
        callable_surface: Optional[Dict[str, Any]] = None,
        state_mut: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], str]:
    reach_body = reach_body or {}
    callable_surface = callable_surface or {}
    state_mut = state_mut or {}
    troot = (A.ROOT / target_root) if target_root else A.ROOT
    req = P.detector_requirements(cand.get("detector", ""))
    per_call_checks = req.get("per_call_checks", ["validateBorrowATokenCap"])
    final_fns = req.get("final_invariant_functions", ["validateBorrowATokenIncreaseLteDebtTokenDecrease"])

    # 1. entrypoint defenses (from reachability)
    entrypoint_defenses = []
    for e in reach_body.get("entrypoints", []):
        if e.get("is_interface_decl"):
            continue
        privileged = bool(set(e.get("modifiers", [])) & set(_PRIV))
        entrypoint_defenses.append({
            "function": e.get("function"), "file": e.get("file"), "line": e.get("line"),
            "visibility": e.get("visibility"), "payable": e.get("payable"),
            "modifiers": e.get("modifiers", []),
            "access_control": [m for m in e.get("modifiers", []) if m in _PRIV] or "none",
            "anyone_can_call": not privileged,
        })

    # 2. multicall engine defenses
    set_refs = [r for r in state_mut.get("isMulticall_refs", []) if "true" in _line_text(r)]
    unset_refs = [r for r in state_mut.get("isMulticall_refs", []) if "false" in _line_text(r)]
    self_dc = state_mut.get("self_delegatecall_refs", [])
    multicall_engine_defenses = [
        {"name": "isMulticall flag set before batch", "refs": set_refs or ["(see Multicall multicall)"],
         "effect": "raises isMulticall=true so per-call checks can branch"},
        {"name": "isMulticall flag unset after batch", "refs": unset_refs, "effect": "lowers flag after final check"},
        {"name": "self-delegatecall target restriction", "refs": self_dc,
         "effect": "Address.functionDelegateCall(address(this), data[i]) — calls only this contract; no arbitrary target",
         "note": "self-delegatecall carries no value; nested multicall possible=unknown (a sub-call could be multicall)"},
        {"name": "batch atomicity", "effect": "functionDelegateCall reverts on sub-call failure -> whole batch reverts"},
        {"name": "final invariant after batch", "refs": state_mut.get("final_invariant_refs", []),
         "effect": f"{final_fns[0] if final_fns else '?'} runs once after all sub-calls"},
    ]

    # 3. isMulticall-dependent branches (the heart)
    is_multicall_branches = []
    checks_skipped: List[str] = []
    for ref in state_mut.get("isMulticall_refs", []):
        rel, _, ln_s = ref.rpartition(":")
        try:
            ln = int(ln_s)
        except ValueError:
            continue
        code = _surrounding(rel, ln)
        low = code.lower()
        kind, skipped_check, normal, mc, replaces, coverage = _classify_branch(code, rel, final_fns)
        if skipped_check:
            checks_skipped.append(skipped_check)
        is_multicall_branches.append({
            "file": rel, "line": ln, "surrounding_code": code, "branch_kind": kind,
            "check_skipped_or_changed": skipped_check,
            "normal_single_call_behavior": normal, "multicall_behavior": mc,
            "final_validation_appears_to_replace": replaces, "coverage_status": coverage,
        })

    # 4. accounting defenses
    accounting_defenses = []
    for fn in per_call_checks:
        refs = _grep(troot, f"function {fn}") or _grep(troot, fn)
        accounting_defenses.append({
            "name": fn, "refs": refs, "kind": "per_call_check",
            "what_it_checks": "absolute borrowAToken.totalSupply() vs borrowATokenCap (reverts if above cap)"
            if fn == "validateBorrowATokenCap" else "per-call accounting validation",
            "skipped_in_multicall": fn in " ".join(checks_skipped) or any(fn in c for c in checks_skipped),
        })
    for fn in final_fns:
        refs = _grep(troot, f"function {fn}") or state_mut.get("final_invariant_refs", [])
        accounting_defenses.append({
            "name": fn, "refs": refs, "kind": "final_batch_check",
            "what_it_checks": "relative + conditional: only when after>cap, requires borrow increase <= debt decrease",
            "skipped_in_multicall": False,
        })

    # 5. callable function defenses
    callable_function_defenses = []
    for c in callable_surface.get("callable_subcalls", []):
        callable_function_defenses.append({
            "function": c.get("function"), "file": c.get("file"), "line": c.get("line"),
            "payable": c.get("mutability") == "payable",
            "blocked_in_multicall": c.get("blocked_in_multicall"),
            "reads_writes_accounting": c.get("mutates_accounting"),
            "per_call_validation": c.get("validation_sensitive"),
            "validation_skipped_in_multicall": "unknown",
            "coverage_status": "unknown",
        })

    # guard coverage matrix
    guard_coverage_matrix = []
    for b in is_multicall_branches:
        if b["check_skipped_or_changed"]:
            guard_coverage_matrix.append({
                "check": b["check_skipped_or_changed"], "location": f'{b["file"]}:{b["line"]}',
                "applies_in_multicall": False, "coverage_status": b["coverage_status"],
                "note": "per-call check skipped in multicall; only the final batch check runs",
            })
    for fn in final_fns:
        guard_coverage_matrix.append({
            "check": fn, "location": (state_mut.get("final_invariant_refs") or ["?"])[0],
            "applies_in_multicall": True, "coverage_status": "partially_covers_candidate",
            "note": "different accounting basis (relative/conditional) than the skipped absolute cap check",
        })

    partial_blockers = [f"{fn} (skipped per-call in multicall; replaced by a relative final check)"
                        for fn in per_call_checks]
    # alias keys for the existing dashboard reader
    defenses_alias = []
    for e in entrypoint_defenses:
        defenses_alias.append({"type": "entrypoint_modifier", "name": ", ".join(e["modifiers"]) or "(none)",
                               "location": f'{e["file"]}:{e["line"]}', "coverage": "does_not_cover",
                               "skipped_in_multicall": False})
    for a in accounting_defenses:
        defenses_alias.append({"type": a["kind"], "name": a["name"],
                               "location": (a["refs"] or ["?"])[0],
                               "coverage": "partially_covers" if a["kind"] == "final_batch_check" else "unknown",
                               "skipped_in_multicall": a["skipped_in_multicall"]})

    status = "DEFENSE_MAPPED" if (entrypoint_defenses or is_multicall_branches or accounting_defenses) else "NEEDS_CONTEXT"

    body = {
        "status": status,
        "summary_plain_english": (
            "Entry is the public payable Size.multicall (pause-gated, callable by anyone). Inside the batch "
            "isMulticall=true makes per-call checks branch: the absolute borrow-aToken cap "
            "(validateBorrowATokenCap) is skipped, and only a relative final check "
            "(validateBorrowATokenIncreaseLteDebtTokenDecrease) runs after the batch. Whether that final check "
            "fully covers the skipped absolute cap is NOT determined here — it is the question for the next gates."),
        "entrypoint_defenses": entrypoint_defenses,
        "multicall_engine_defenses": multicall_engine_defenses,
        "is_multicall_branches": is_multicall_branches,
        "accounting_defenses": accounting_defenses,
        "callable_function_defenses": callable_function_defenses,
        "guard_coverage_matrix": guard_coverage_matrix,
        "hard_blockers": [],
        "partial_blockers": partial_blockers,
        "unresolved_assumptions": [
            "Whether non-payable facade siblings are also reachable via self-delegatecall (no value forwarded).",
            "Whether a nested multicall can re-enter or stack isMulticall behavior.",
        ],
        "next_questions": [
            "Does the final relative check permit ending above the absolute cap without a matching debt decrease?",
            "Which callable sub-calls can move borrowAToken up while debtToken does not move down?",
        ],
        # ---- alias keys for existing dashboard reader (no UI change) ----
        "defenses": defenses_alias,
        "checks_skipped_when_isMulticall": sorted(set(checks_skipped)),
    }
    return body, status


def _line_text(ref: str) -> str:
    rel, _, ln_s = ref.rpartition(":")
    try:
        ln = int(ln_s)
    except ValueError:
        return ""
    lines = _lines(rel)
    return lines[ln - 1] if 0 < ln <= len(lines) else ""


def _classify_branch(code: str, rel: str, final_fns: List[str]):
    low = code.lower()
    if "ismulticall = true" in low or "ismulticall=true" in low:
        return ("engine_set", None, "n/a", "flag raised before batch", None, "n/a")
    if "ismulticall = false" in low or "ismulticall=false" in low:
        return ("engine_unset", None, "n/a", "flag lowered after batch", None, "n/a")
    if re.search(r"if\s*\(\s*!\s*[\w.]*ismulticall", low):
        # the skipped check is the call guarded BY the `if (!isMulticall)` line — search from that line forward,
        # preferring a validate*/cap* call (not an earlier unrelated state.x() in the context window)
        clines = code.splitlines()
        gi = next((k for k, l in enumerate(clines)
                   if re.search(r"if\s*\(\s*!\s*[\w.]*ismulticall", l.lower())), 0)
        after = "\n".join(clines[gi:gi + 4])
        m = (re.search(r"\b(validate\w+)\b", after) or re.search(r"state\.(\w+)\(", after)
             or re.search(r"\b(validate\w+)\b", code))
        skipped = m.group(1) if m else "a per-call check"
        return ("skip_in_multicall", skipped,
                f"{skipped} runs (enforced per call)",
                f"{skipped} is SKIPPED during multicall",
                (final_fns[0] if final_fns else None) + " (different basis)" if final_fns else None,
                "partially_covers_candidate")
    if re.search(r"if\s*\(\s*[\w.]*ismulticall", low):
        return ("multicall_only_branch", None, "branch not taken", "multicall-specific branch taken", None, "unknown")
    return ("reference", None, "n/a", "n/a", None, "unknown")
