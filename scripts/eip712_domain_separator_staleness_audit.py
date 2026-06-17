#!/usr/bin/env python3
"""
eip712_domain_separator_staleness_audit.py — EIP-712 DOMAIN_SEPARATOR STALENESS research lens (read-only,
is_gate:false, NOT wired into routing). Generalized class of the P304 centrifuge M-03 miss. Anchored on
centrifuge token/ERC20.sol.

Per-contract: gathers the constructor body, any *domain*/_calculateDomainSeparator helper bodies (for the
name/version reference), and all non-ctor function bodies (for a post-ctor name mutator), then runs
eip712_domain_separator_staleness_taxonomy.classify_contract(). Writes output/eip712_domain_separator_staleness_audit.json.

RESEARCH-ONLY: NEVER mints findings, NEVER routes. routed_manifest_ids is always empty. High precision over recall.

Usage: python scripts/eip712_domain_separator_staleness_audit.py [--manifest <path>] [--no-source] [--quiet]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
import eip712_domain_separator_staleness_taxonomy as eds  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
_FILE_CACHE: dict[str, list[str]] = {}
_BODY_MAX_LINES = 400


def _load(path: Path, key: str) -> list:
    try:
        d = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return []
    return d.get(key, []) if isinstance(d, dict) else d


def _function_body(file_rel, start, use_source) -> str:
    if not use_source or not file_rel or not start:
        return ""
    if file_rel not in _FILE_CACHE:
        try:
            _FILE_CACHE[file_rel] = (ROOT / file_rel).read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            _FILE_CACHE[file_rel] = []
    lines = _FILE_CACHE[file_rel]
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
    return "\n".join(out)[:8000]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest")
    ap.add_argument("--no-source", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    man_path = Path(args.manifest) if args.manifest else audit_path("output") / "coverage_manifest.json"
    items = _load(man_path, "items")
    if not items:
        raise SystemExit(f"[eip712_domain_separator_staleness_audit] no manifest items at {man_path}")
    use_source = not args.no_source

    fn_items = [it for it in items if it.get("kind") in ("function", "initializer", "constructor")]
    in_scope_ids = {it["id"] for it in items if it.get("in_scope", True)}
    bodies: dict[str, dict[str, str]] = defaultdict(dict)
    ctor_item: dict[str, dict] = {}
    for it in fn_items:
        span = it.get("source_span", {})
        c, n = it.get("contract", ""), it.get("name", "")
        bodies[c][n] = _function_body(it.get("file", ""), span.get("start_line"), use_source)
        if it.get("kind") == "constructor" or n.lower() in ("constructor", c.lower()):
            ctor_item[c] = it

    candidates = []
    for contract, fnmap in bodies.items():
        ctor_name = next((n for n in fnmap if n.lower() in ("constructor", contract.lower())), None)
        ctor_body = fnmap.get(ctor_name, "") if ctor_name else ""
        if not ctor_body:
            continue
        # calc_blob = ctor + any *domain* helper bodies (so keccak256(bytes(name)) inside _calculateDomainSeparator is seen)
        calc_blob = ctor_body + "\n" + "\n".join(
            b for nm, b in fnmap.items() if "domain" in nm.lower())
        # mutator_blob = all NON-ctor bodies (for a post-ctor name setter / file('name'))
        mutator_blob = "\n".join(b for nm, b in fnmap.items() if nm != ctor_name)
        for c in eds.classify_contract(contract, ctor_body, calc_blob, mutator_blob):
            it = ctor_item.get(contract, {})
            span = it.get("source_span", {})
            mid = it.get("id")
            c.update({"contract": contract, "function": ctor_name or "constructor", "file": it.get("file"),
                      "lens_id": f"{contract}:{c['finding_shape']}",
                      "in_scope": mid in in_scope_ids if mid else True, "manifest_id": mid,
                      "file_line_refs": f"{it.get('file','')}:{span.get('start_line','')}",
                      "false_positive_controls": "two-signal (cached-separator-from-name + mutable-name); "
                                                 "name-fixed-in-ctor / live-separator / library suppressed"})
            candidates.append(c)

    by_conf = Counter(c["confidence"] for c in candidates)
    report = {
        "lens": "eip712_domain_separator_staleness",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "manifest": str(man_path), "is_gate": False, "research_only": False, "promotion": "advisory_only", "routes_in_production": False,
        "raw_candidates": len(candidates), "by_confidence": dict(by_conf),
        "high": by_conf.get("high", 0), "medium": by_conf.get("medium", 0), "low": by_conf.get("low", 0),
        "routed_manifest_ids": [],          # research-only — never routes
        "candidates": candidates,
    }
    out = audit_path("output") / "eip712_domain_separator_staleness_audit.json"
    out.write_text(json.dumps(report, indent=2))
    if not args.quiet:
        print(f"[eip712_domain_separator_staleness_audit] RESEARCH-ONLY (no routing) · candidates {len(candidates)} "
              f"· high {report['high']} medium {report['medium']} · wrote {out}")
        for c in candidates:
            print(f"   • {c['contract']} [{c['confidence']}] {c['finding_shape']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
