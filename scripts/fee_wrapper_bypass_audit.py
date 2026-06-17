#!/usr/bin/env python3
"""
fee_wrapper_bypass_audit.py — FEE-WRAPPER BYPASS research lens (CONSERVATIVE / low-precision, read-only,
is_gate:false, NOT wired into routing). Generalized class of the P306 decent M-02 miss. Anchored on decent
DecentEthRouter.bridge/bridgeWithPayload (public) + UTBFeeCollector.

Computes a scope-level has_fee_layer flag (any *FeeCollector* contract or collectFees-style fn across the manifest),
then per-function (with +1-level helper resolve) emits low-confidence candidates for public, unguarded cross-chain
actions that do not themselves collect fees. Writes output/fee_wrapper_bypass_audit.json.

RESEARCH-ONLY: NEVER mints findings, NEVER routes. routed_manifest_ids is always empty.

Usage: python scripts/fee_wrapper_bypass_audit.py [--manifest <path>] [--no-source] [--quiet]
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
import fee_wrapper_bypass_taxonomy as fwb  # noqa: E402

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
        raise SystemExit(f"[fee_wrapper_bypass_audit] no manifest items at {man_path}")
    use_source = not args.no_source

    fn_items = [it for it in items if it.get("kind") in ("function", "initializer", "constructor")]
    in_scope_ids = {it["id"] for it in items if it.get("in_scope", True)}
    bodies_by_contract: dict[str, dict[str, str]] = defaultdict(dict)
    for it in fn_items:
        span = it.get("source_span", {})
        bodies_by_contract[it.get("contract", "")][it.get("name", "")] = \
            _function_body(it.get("file", ""), span.get("start_line"), use_source)

    # ---- S1 (scope-level): does the codebase have a fee layer? ----
    has_fee_layer = False
    for contract, fnmap in bodies_by_contract.items():
        if fwb.is_fee_layer_contract(contract, " ".join(fnmap.keys()) + " " + " ".join(fnmap.values())):
            has_fee_layer = True
            break

    candidates = []
    for it in fn_items:
        name, contract, mid = it.get("name", ""), it.get("contract", ""), it.get("id")
        body = bodies_by_contract[contract].get(name, "")
        resolved = body
        for called in set(_LOCAL_CALL_RE.findall(body)):
            if called != name and called in bodies_by_contract[contract]:
                resolved += "\n" + bodies_by_contract[contract][called]
        for c in fwb.classify(name, it.get("signature", ""), it.get("file", ""), contract, snippet=resolved,
                              kind=it.get("kind", "function"), tags=it.get("tags"),
                              has_fee_layer=has_fee_layer, visibility=it.get("visibility", "")):
            span = it.get("source_span", {})
            c.update({"contract": contract, "function": name, "file": it.get("file"),
                      "lens_id": f"{contract}:{name}:{c['finding_shape']}",
                      "in_scope": mid in in_scope_ids, "manifest_id": mid,
                      "visibility": it.get("visibility", ""),
                      "file_line_refs": f"{it.get('file','')}:{span.get('start_line','')}",
                      "false_positive_controls": "scope fee-layer + public unguarded cross-chain action not "
                                                 "collecting fees; access-modifier/fee-invoker/no-fee-layer/view suppressed"})
            candidates.append(c)

    seen, uniq = set(), []
    for c in candidates:
        if c["lens_id"] in seen:
            continue
        seen.add(c["lens_id"]); uniq.append(c)
    candidates = uniq

    report = {
        "lens": "fee_wrapper_bypass",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "manifest": str(man_path), "is_gate": False, "research_only": False, "promotion": "advisory_only", "routes_in_production": False,
        "has_fee_layer": has_fee_layer, "raw_candidates": len(candidates),
        "high": 0, "medium": 0, "low": len(candidates),
        "routed_manifest_ids": [],
        "candidates": candidates,
    }
    out = audit_path("output") / "fee_wrapper_bypass_audit.json"
    out.write_text(json.dumps(report, indent=2))
    if not args.quiet:
        print(f"[fee_wrapper_bypass_audit] RESEARCH-ONLY (no routing) · fee_layer={has_fee_layer} · candidates "
              f"{len(candidates)} (low) · wrote {out}")
        for c in candidates:
            print(f"   • {c['contract']}.{c['function']} [low] fee_wrapper_bypass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
