#!/usr/bin/env python3
"""
nonstandard_permit_audit.py — NON-STANDARD PERMIT research lens (read-only, is_gate:false, NOT wired into routing).
Generalized class of the P302 pooltogether M-08 miss (hard-coded EIP-2612 permit on a configurable asset -> reverts
for DAI/non-2612 assets). Anchored on PrizeVault.depositWithPermit.

Function-scoped: for each manifest function it brace-matches the body (+1-level same-contract helper resolution),
runs nonstandard_permit_taxonomy.classify(), and emits candidates. Writes output/nonstandard_permit_audit.json.

RESEARCH-ONLY: NEVER mints findings, NEVER routes. routed_manifest_ids is always empty. High precision over recall.

Usage: python scripts/nonstandard_permit_audit.py [--manifest <path>] [--no-source] [--quiet]
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
import nonstandard_permit_taxonomy as nsp  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
_FILE_CACHE: dict[str, list[str]] = {}
_BODY_MAX_LINES = 400
_LOCAL_CALL_RE = re.compile(r"(?<![.\w])([A-Za-z_]\w*)\s*\(")


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
        raise SystemExit(f"[nonstandard_permit_audit] no manifest items at {man_path}")
    use_source = not args.no_source

    fn_items = [it for it in items if it.get("kind") in ("function", "initializer", "constructor")]
    in_scope_ids = {it["id"] for it in items if it.get("in_scope", True)}
    bodies_by_contract: dict[str, dict[str, str]] = defaultdict(dict)
    for it in fn_items:
        span = it.get("source_span", {})
        bodies_by_contract[it.get("contract", "")][it.get("name", "")] = \
            _function_body(it.get("file", ""), span.get("start_line"), use_source)

    candidates = []
    for it in fn_items:
        name, contract, mid = it.get("name", ""), it.get("contract", ""), it.get("id")
        body = bodies_by_contract[contract].get(name, "")
        if not nsp.has_permit_consumption(body):     # S1 must be in the function's OWN body
            continue
        resolved = body
        for called in set(_LOCAL_CALL_RE.findall(body)):
            if called != name and called in bodies_by_contract[contract]:
                resolved += "\n" + bodies_by_contract[contract][called]
        for c in nsp.classify(name, it.get("signature", ""), it.get("file", ""), contract, snippet=resolved,
                              kind=it.get("kind", "function"), tags=it.get("tags")):
            span = it.get("source_span", {})
            c.update({"contract": contract, "function": name, "file": it.get("file"),
                      "lens_id": f"{contract}:{name}:{c['finding_shape']}",
                      "in_scope": mid in in_scope_ids, "manifest_id": mid,
                      "visibility": it.get("visibility", ""),
                      "file_line_refs": f"{it.get('file','')}:{span.get('start_line','')}",
                      "false_positive_controls": "three-signal gate (2612-permit-consume + configurable/external "
                                                 "asset + missing-resilience); self-token/router/library/"
                                                 "Permit2-or-try-catch suppressed"})
            candidates.append(c)

    seen, uniq = set(), []
    for c in candidates:
        if c["lens_id"] in seen:
            continue
        seen.add(c["lens_id"]); uniq.append(c)
    candidates = uniq

    by_conf = Counter(c["confidence"] for c in candidates)
    report = {
        "lens": "nonstandard_permit", "shape": "nonstandard_permit_hardcoded",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "manifest": str(man_path), "is_gate": False, "research_only": False, "promotion": "advisory_only", "routes_in_production": False,
        "raw_candidates": len(candidates), "by_confidence": dict(by_conf),
        "high": by_conf.get("high", 0), "medium": by_conf.get("medium", 0), "low": by_conf.get("low", 0),
        "routed_manifest_ids": [],          # research-only — never routes
        "candidates": candidates,
    }
    out = audit_path("output") / "nonstandard_permit_audit.json"
    out.write_text(json.dumps(report, indent=2))

    if not args.quiet:
        print(f"[nonstandard_permit_audit] RESEARCH-ONLY (no routing) · candidates {len(candidates)} "
              f"· high {report['high']} medium {report['medium']} low {report['low']} · wrote {out}")
        for c in candidates:
            print(f"   • {c['contract']}.{c['function']} [{c['confidence']}] asset={c['permitted_asset_source']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
