"""
Gate 1 — source_resolve_gate.

Confirms the candidate's source file + function exist, captures the function signature, line range, a brace-matched
snippet, and a source hash. Read-only.

PASS  -> RESOLVED_SOURCE
NEEDS_CONTEXT -> file/function cannot be resolved
KILLED -> file present but the named function is clearly absent (stale/mismatched candidate)
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import artifacts as A  # noqa: E402

_MAX_LINES = 200


def _resolve_abs(file_rel: Optional[str], target_root: Optional[str], roots: List[Path]) -> Optional[Path]:
    if not file_rel:
        return None
    candidates: List[Path] = []
    if target_root:
        candidates.append(A.ROOT / target_root / file_rel)
    for r in roots:
        candidates.append(Path(r) / file_rel)
    candidates.append(A.ROOT / file_rel)
    for c in candidates:
        try:
            p = c.resolve()
        except (OSError, ValueError):
            continue
        if p.is_file() and (A.ROOT.resolve() in p.parents or p == A.ROOT.resolve()):
            return p
    return None


def extract_function(lines: List[str], fn_name: str, hint_line: Optional[int]) -> Optional[Dict[str, Any]]:
    """Find `function <fn_name>(` (nearest to hint_line, 1-indexed), capture signature + brace-matched body."""
    pat = re.compile(r"\bfunction\s+" + re.escape(fn_name) + r"\s*\(")
    matches = [i for i, ln in enumerate(lines) if pat.search(ln)]
    if not matches:
        return None
    if hint_line is not None:
        matches.sort(key=lambda i: abs((i + 1) - hint_line))
    start = matches[0]
    # signature spans from `function` to the first '{'
    sig_end = start
    for j in range(start, min(start + 30, len(lines))):
        if "{" in lines[j]:
            sig_end = j
            break
    else:
        sig_end = start
    signature = "\n".join(lines[start:sig_end + 1]).strip()
    # brace match from the opening '{'
    depth = 0
    started = False
    end = sig_end
    for j in range(sig_end, min(sig_end + _MAX_LINES, len(lines))):
        for ch in lines[j]:
            if ch == "{":
                depth += 1
                started = True
            elif ch == "}":
                depth -= 1
        end = j
        if started and depth <= 0:
            break
    snippet = "\n".join(lines[start:end + 1])
    return {"start_line": start + 1, "end_line": end + 1, "signature": signature, "snippet": snippet}


def run(cand: Dict[str, Any], target_root: Optional[str], roots: Optional[List[Path]] = None) -> Tuple[Dict[str, Any], str]:
    roots = roots or A.source_roots()
    file_rel = cand.get("file")
    fn_name = cand.get("function")
    hint = cand.get("line")
    abs_path = _resolve_abs(file_rel, target_root, roots)

    if abs_path is None:
        body = {
            "resolved_abs_path": None, "function_signature": None, "line_range": None,
            "snippet_match": False, "code_snippet": None, "source_hash": None,
            "resolution_status": "unresolved",
        }
        return body, "NEEDS_CONTEXT"

    src_hash = A.md5_file(abs_path)
    lines = abs_path.read_text(encoding="utf-8", errors="replace").splitlines()
    fn = extract_function(lines, fn_name, hint) if fn_name else None

    if fn is None:
        body = {
            "resolved_abs_path": str(abs_path), "function_signature": None, "line_range": None,
            "snippet_match": False, "code_snippet": None, "source_hash": src_hash,
            "resolution_status": "function_not_found",
        }
        # file present but function absent -> stale/mismatched candidate
        return body, "KILLED"

    body = {
        "resolved_abs_path": str(abs_path),
        "function_signature": fn["signature"],
        "line_range": [fn["start_line"], fn["end_line"]],
        "snippet_match": True,
        "code_snippet": fn["snippet"],
        "source_hash": src_hash,
        "resolution_status": "resolved",
    }
    return body, "RESOLVED_SOURCE"
