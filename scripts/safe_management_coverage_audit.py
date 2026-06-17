#!/usr/bin/env python3
"""
safe_management_coverage_audit.py — SAFE-MANAGEMENT COVERAGE research prototype (read-only, is_gate:false, NOT
wired into routing). Flags guard/policy contracts that protect a Gnosis Safe but decode a Safe self-management
selector at the wrong calldata offset, or leave high-impact Safe self-management selectors uncovered.

Per contract it (1) assembles the contract's guard logic (all of its function bodies), (2) resolves bytes4
selector + calldata-offset `constant`s declared across in-scope source, then (3) runs
safe_management_coverage_taxonomy.classify(). Writes <out>/safe_management_coverage_audit.json.

RESEARCH-ONLY: NEVER mints findings, NEVER routes. routed_manifest_ids is always empty. High precision over recall.

Usage: python scripts/safe_management_coverage_audit.py [--manifest <path>] [--out <path>] [--no-source] [--quiet]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
import safe_management_coverage_taxonomy as smc  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
_FILE_CACHE: dict[str, list[str]] = {}
_BODY_MAX_LINES = 400
_CONST_RE = re.compile(r"constant\s+([A-Za-z_]\w*)\s*=\s*([^;]+);")


def _load(path: Path, key: str) -> list:
    try:
        d = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return []
    return d.get(key, []) if isinstance(d, dict) else d


def _lines(file_rel: str) -> list[str]:
    if file_rel not in _FILE_CACHE:
        try:
            _FILE_CACHE[file_rel] = (ROOT / file_rel).read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            _FILE_CACHE[file_rel] = []
    return _FILE_CACHE[file_rel]


def _function_body(file_rel, start, use_source) -> str:
    if not use_source or not file_rel or not start:
        return ""
    lines = _lines(file_rel)
    if not lines:
        return ""
    i = max(0, (start or 1) - 1)
    n = len(lines)
    j = i
    while j < min(n, i + 25) and "{" not in lines[j]:
        j += 1
    if j >= min(n, i + 25) or "{" not in lines[j]:
        return ""
    depth, out, started = 0, [], False
    for k in range(j, min(n, j + _BODY_MAX_LINES)):
        line = lines[k]
        out.append(line)
        depth += line.count("{") - line.count("}")
        if "{" in line:
            started = True
        if started and depth <= 0:
            break
    return "\n".join(out)[:12000]


def _resolve_constants(files: set[str], use_source: bool) -> dict:
    """Scan in-scope source files for `... constant NAME = VALUE;` -> {name.lower(): value-string}."""
    consts: dict[str, str] = {}
    if not use_source:
        return consts
    for f in files:
        text = "\n".join(_lines(f))
        for m in _CONST_RE.finditer(text):
            consts[m.group(1).lower()] = m.group(2).strip()
    return consts


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest")
    ap.add_argument("--out")
    ap.add_argument("--no-source", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    man_path = Path(args.manifest) if args.manifest else audit_path("output") / "coverage_manifest.json"
    items = _load(man_path, "items")
    if not items:
        raise SystemExit(f"[safe_management_coverage_audit] no manifest items at {man_path}")
    use_source = not args.no_source

    in_scope_ids = {it["id"] for it in items if it.get("in_scope", True)}

    def _is_test_path(f: str) -> bool:
        fl = (f or "").lower()
        return ("/test/" in fl or "/tests/" in fl or "/mocks/" in fl or fl.endswith(".t.sol")
                or "/mock" in fl)

    # Guard-coverage analysis only makes sense on in-scope, non-test contracts (a guard the protocol ships).
    fn_items = [it for it in items
                if it.get("kind") in ("function", "initializer", "constructor")
                and it.get("id") in in_scope_ids
                and not _is_test_path(it.get("file", ""))]

    # assemble per-contract guard logic (concatenate the contract's function bodies) + collect files + meta
    bodies_by_contract: dict[str, list[str]] = defaultdict(list)
    meta_by_contract: dict[str, dict] = {}
    files: set[str] = set()
    for it in fn_items:
        c = it.get("contract", "")
        span = it.get("source_span", {})
        body = _function_body(it.get("file", ""), span.get("start_line"), use_source)
        if body:
            bodies_by_contract[c].append(body)
        if it.get("file"):
            files.add(it["file"])
        m = meta_by_contract.setdefault(c, {"file": it.get("file", ""), "first_line": span.get("start_line"),
                                            "in_scope": False, "manifest_id": it.get("id")})
        if it.get("id") in in_scope_ids:
            m["in_scope"] = True

    # Resolve selector/offset `constant`s from ALL non-test source (selector/offset constants typically live in a
    # shared library that is out-of-scope, e.g. reNFT RentalConstants.sol), even though we only CLASSIFY in-scope
    # guard contracts.
    all_files = {it["file"] for it in items if it.get("file") and not _is_test_path(it.get("file", ""))}
    constants = _resolve_constants(all_files or files, use_source)

    candidates = []
    for contract, bodies in bodies_by_contract.items():
        guard_body = "\n".join(bodies)
        for c in smc.classify(contract, guard_body, constants=constants):
            m = meta_by_contract.get(contract, {})
            c.update({
                "contract": contract,
                "file": m.get("file", ""),
                "file_line_refs": f"{m.get('file','')}:{m.get('first_line','')}",
                "in_scope": m.get("in_scope", True),
                "manifest_id": m.get("manifest_id"),
                "lens_id": f"{contract}:{c['finding_shape']}:{c.get('selector','')}",
                "false_positive_controls": "two-signal (Safe-guard selector-filter context + >=1 Safe self-mgmt "
                                           "selector covered) AND a concrete defect (decode-offset mismatch OR "
                                           "missing high-impact selector); admin-only downgraded; non-guard suppressed",
            })
            candidates.append(c)

    seen, uniq = set(), []
    for c in candidates:
        if c["lens_id"] in seen:
            continue
        seen.add(c["lens_id"]); uniq.append(c)
    candidates = uniq

    by_conf = Counter(c["confidence"] for c in candidates)
    by_shape = Counter(c["finding_shape"] for c in candidates)
    report = {
        "lens": "safe_management_coverage",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "manifest": str(man_path),
        "is_gate": False, "research_only": True, "routes_in_production": False,
        "routed_manifest_ids": [],          # research-only — never routes
        "raw_candidates": len(candidates),
        "by_confidence": dict(by_conf),
        "by_shape": dict(by_shape),
        "high": by_conf.get("high", 0), "medium": by_conf.get("medium", 0), "low": by_conf.get("low", 0),
        "candidates": candidates,
    }
    out = Path(args.out) if args.out else audit_path("output") / "safe_management_coverage_audit.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))

    if not args.quiet:
        print(f"[safe_management_coverage_audit] RESEARCH-ONLY (no routing) · candidates {len(candidates)} "
              f"· high {report['high']} medium {report['medium']} low {report['low']} · wrote {out}")
        for c in candidates:
            print(f"   • {c['contract']} [{c['confidence']}] {c['finding_shape']} :: {c.get('selector','')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
