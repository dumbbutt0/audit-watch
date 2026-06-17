#!/usr/bin/env python3
"""
multicall_invariant_audit.py — MULTICALL / BATCH-INVARIANT research prototype (read-only, is_gate:false, NOT
wired into routing). Seeded by the Size Credit eval (M-01: Multicall.multicall validates the borrow-aToken cap
with balanceOf(address(this)) instead of totalSupply()).

Function-scoped: for each manifest function, it brace-matches the body (+ one level of same-contract helper
resolution so a delegatecall/validate in a called helper is credited), runs
multicall_invariant_taxonomy.classify(), and emits candidates. Writes output/multicall_invariant_audit.json.

RESEARCH-ONLY: NEVER mints findings, NEVER routes. `routed_manifest_ids` is always empty; there is no advisory
escalation, no gate wiring, and no run_pipeline integration. This detector exists to measure recall on the
multicall/batch-invariant family before any promotion decision.

Usage: python scripts/multicall_invariant_audit.py [--manifest <path>] [--no-source] [--quiet]
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
import multicall_invariant_taxonomy as mci  # noqa: E402

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
    while j < min(n, i + 25) and "{" not in lines[j]:   # tolerate multi-line signatures before `{`
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
    ap.add_argument("--inherited-sidecar", dest="inherited_sidecar",
                    help="RESEARCH-ONLY: merge an isolated inherited-multicall sidecar (B1 visibility) into the "
                         "detector input for THIS run only. Never written back; canonical manifest untouched.")
    args = ap.parse_args()

    man_path = Path(args.manifest) if args.manifest else audit_path("output") / "coverage_manifest.json"
    items = _load(man_path, "items")
    if not items:
        raise SystemExit(f"[multicall_invariant_audit] no manifest items at {man_path}")
    # RESEARCH-ONLY optional merge: inherited-multicall sidecar (B1). Gated entirely behind the flag so that
    # without it behavior is byte-for-byte identical. Sidecar items are tagged source_kind:inherited_multicall_
    # sidecar and are merged into the in-memory item list ONLY — the canonical manifest is never mutated/rewritten.
    sidecar_ids: set = set()
    if args.inherited_sidecar:
        sidecar_items = _load(Path(args.inherited_sidecar), "items")
        for s in sidecar_items:
            if isinstance(s, dict) and s.get("id"):
                sidecar_ids.add(s["id"])
        items = list(items) + list(sidecar_items)
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
        # +1-level same-contract helper resolution (credit a delegatecall/validate in a called helper)
        resolved = body
        for called in set(_LOCAL_CALL_RE.findall(body)):
            if called != name and called in bodies_by_contract[contract]:
                resolved += "\n" + bodies_by_contract[contract][called]
        for c in mci.classify(name, it.get("signature", ""), it.get("file", ""), contract, snippet=resolved,
                              tags=it.get("tags")):
            span = it.get("source_span", {})
            c.update({"contract": contract, "function": name, "file": it.get("file"),
                      "lens_id": f"{contract}:{name}:{c['finding_shape']}",
                      "in_scope": mid in in_scope_ids, "manifest_id": mid,
                      "visibility": it.get("visibility", ""),
                      "file_line_refs": f"{it.get('file','')}:{span.get('start_line','')}",
                      "false_positive_controls": "two-signal gate (batch-executor + accounting-invariant); "
                                                 "pure-view/admin-setter/thin-wrapper/non-executing-loop suppressed"})
            # RESEARCH-ONLY: candidates derived from a merged inherited-multicall sidecar entry carry their
            # synthetic/inherited provenance and the un-routed safety flags so downstream readers can never
            # mistake a visibility-attributed executor for a real, in-manifest finding.
            if mid in sidecar_ids:
                c.update({"synthetic_attribution": True, "source_kind": "inherited_multicall_sidecar",
                          "research_only": True, "routes_in_production": False, "routed_manifest_ids": [],
                          "base_contract": it.get("base_contract"), "base_source_file": it.get("base_source_file"),
                          "target_file": it.get("target_file"),
                          "attribution_reason": it.get("attribution_reason")})
            candidates.append(c)

    # de-dup identical lens_ids
    seen, uniq = set(), []
    for c in candidates:
        if c["lens_id"] in seen:
            continue
        seen.add(c["lens_id"]); uniq.append(c)
    candidates = uniq

    by_conf = Counter(c["confidence"] for c in candidates)
    report = {
        "lens": "multicall_invariant", "generated_at": datetime.now(timezone.utc).isoformat(),
        "manifest": str(man_path), "is_gate": False, "research_only": True, "routes_in_production": False,
        "raw_candidates": len(candidates),
        "by_shape": dict(Counter(c["finding_shape"] for c in candidates)),
        "by_confidence": dict(by_conf),
        "high": by_conf.get("high", 0), "medium": by_conf.get("medium", 0),
        "low": by_conf.get("low", 0), "needs_context": by_conf.get("needs_context", 0),
        "routed_manifest_ids": [],          # research-only — never routes
        "candidates": candidates,
    }
    # Only surface sidecar provenance keys when a sidecar was actually merged, so the default (no-sidecar)
    # report stays byte-for-byte identical to prior behavior.
    if args.inherited_sidecar:
        report["inherited_sidecar"] = str(Path(args.inherited_sidecar))
        report["sidecar_candidates"] = sum(1 for c in candidates if c.get("manifest_id") in sidecar_ids)
    out = audit_path("output") / "multicall_invariant_audit.json"
    out.write_text(json.dumps(report, indent=2))

    if not args.quiet:
        print(f"[multicall_invariant_audit] RESEARCH-ONLY (no routing) · candidates {len(candidates)} "
              f"· high {report['high']} medium {report['medium']} needs_context {report['needs_context']} "
              f"· wrote {out}")
        for c in candidates:
            print(f"   • {c['contract']}.{c['function']} [{c['finding_shape']}/{c['confidence']}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
