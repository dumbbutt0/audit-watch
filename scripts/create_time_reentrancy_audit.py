#!/usr/bin/env python3
"""
create_time_reentrancy_audit.py — CREATE-TIME REENTRANCY research prototype (read-only, is_gate:false, un-wired).
Per manifest function it brace-matches the body (+1-level same-contract helper resolution so an inlined
`_mintProcessing`/`_safeMint` helper is seen), runs create_time_reentrancy_taxonomy.classify(), dedups one per
(contract, function). Writes <out>/create_time_reentrancy_audit.json.

RESEARCH-ONLY: NEVER mints/routes. routed_manifest_ids always empty. High precision over recall.
Usage: python scripts/create_time_reentrancy_audit.py [--manifest <path>] [--out <path>] [--no-source] [--quiet]
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
import create_time_reentrancy_taxonomy as ctr  # noqa: E402

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
    return "\n".join(out)[:12000]


def _is_test_path(f: str) -> bool:
    fl = (f or "").lower()
    return ("/test/" in fl or "/tests/" in fl or "/mocks/" in fl or fl.endswith(".t.sol") or "/mock" in fl)


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
        raise SystemExit(f"[create_time_reentrancy_audit] no manifest items at {man_path}")
    use_source = not args.no_source

    in_scope_ids = {it["id"] for it in items if it.get("in_scope", True)}
    fn_items = [it for it in items
                if it.get("kind") in ("function", "initializer", "constructor")
                and it.get("id") in in_scope_ids and not _is_test_path(it.get("file", ""))]

    bodies_by_contract: dict[str, dict[str, str]] = defaultdict(dict)
    for it in fn_items:
        span = it.get("source_span", {})
        bodies_by_contract[it.get("contract", "")][it.get("name", "")] = \
            _function_body(it.get("file", ""), span.get("start_line"), use_source)

    candidates = []
    for it in fn_items:
        name, contract, mid = it.get("name", ""), it.get("contract", ""), it.get("id")
        body = bodies_by_contract[contract].get(name, "")
        if not body:
            continue
        resolved = body
        for called in set(_LOCAL_CALL_RE.findall(body)):
            if called != name and called in bodies_by_contract[contract]:
                resolved += "\n" + bodies_by_contract[contract][called]
        for c in ctr.classify(contract, name, it.get("signature", ""), resolved, modifiers=it.get("modifiers")):
            span = it.get("source_span", {})
            c.update({
                "contract": contract, "function": name, "file": it.get("file"),
                "lens_id": f"{contract}:{name}:create_time_reentrancy",
                "in_scope": mid in in_scope_ids, "manifest_id": mid,
                "file_line_refs": f"{it.get('file','')}:{span.get('start_line','')}",
                "false_positive_controls": "four-signal (create-verb fn + callback-yielding interaction + state-commit "
                                           "AFTER callback (ordering) + no nonReentrant guard); guarded/CEI-correct "
                                           "suppressed; cross-contract stale-check + Seaport-mediated are blind spots",
            })
            candidates.append(c)

    seen, uniq = set(), []
    for c in candidates:
        if c["lens_id"] in seen:
            continue
        seen.add(c["lens_id"]); uniq.append(c)
    candidates = uniq

    by_conf = Counter(c["confidence"] for c in candidates)
    report = {
        "lens": "create_time_reentrancy",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "manifest": str(man_path),
        "is_gate": False, "research_only": True, "routes_in_production": False,
        "routed_manifest_ids": [],
        "raw_candidates": len(candidates),
        "by_confidence": dict(by_conf),
        "high": by_conf.get("high", 0), "medium": by_conf.get("medium", 0), "low": by_conf.get("low", 0),
        "candidates": candidates,
    }
    out = Path(args.out) if args.out else audit_path("output") / "create_time_reentrancy_audit.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))

    if not args.quiet:
        print(f"[create_time_reentrancy_audit] RESEARCH-ONLY · candidates {len(candidates)} "
              f"· high {report['high']} medium {report['medium']} · wrote {out}")
        for c in candidates:
            print(f"   • {c['contract']}.{c['function']} [{c['confidence']}] {c['create_verb']} :: {c['callback']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
