#!/usr/bin/env python3
"""
hostile_token_settlement_audit.py — HOSTILE-TOKEN SETTLEMENT research prototype (read-only, is_gate:false, NOT
wired into routing). Flags must-succeed settlement/cleanup flows that push an attacker-/user-selected token with no
containment, so a hostile token can block the cleanup (permanent lock / DoS).

Per manifest function it brace-matches the body (+1-level same-contract helper resolution so an inlined
`_settlePayment`/`_safeTransfer`/`_transferERC721` helper is seen), runs hostile_token_settlement_taxonomy.classify(),
and dedups to one candidate per (contract, shape). Writes <out>/hostile_token_settlement_audit.json.

RESEARCH-ONLY: NEVER mints findings, NEVER routes. routed_manifest_ids is always empty. High precision over recall.

Usage: python scripts/hostile_token_settlement_audit.py [--manifest <path>] [--out <path>] [--no-source] [--quiet]
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
import hostile_token_settlement_taxonomy as hts  # noqa: E402

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
        raise SystemExit(f"[hostile_token_settlement_audit] no manifest items at {man_path}")
    use_source = not args.no_source

    in_scope_ids = {it["id"] for it in items if it.get("in_scope", True)}
    fn_items = [it for it in items
                if it.get("kind") in ("function", "initializer", "constructor")
                and it.get("id") in in_scope_ids
                and not _is_test_path(it.get("file", ""))]

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
        # +1-level same-contract helper resolution (so settle/reclaim helpers' transfers are visible)
        resolved = body
        for called in set(_LOCAL_CALL_RE.findall(body)):
            if called != name and called in bodies_by_contract[contract]:
                resolved += "\n" + bodies_by_contract[contract][called]
        for c in hts.classify(contract, name, it.get("signature", ""), resolved):
            span = it.get("source_span", {})
            c.update({
                "contract": contract, "function": name, "file": it.get("file"),
                "lens_id": f"{contract}:{c['finding_shape']}",  # dedup one per contract+shape
                "in_scope": mid in in_scope_ids, "manifest_id": mid,
                "file_line_refs": f"{it.get('file','')}:{span.get('start_line','')}",
                "false_positive_controls": "five-signal (cleanup-verb fn + must-succeed token push + attacker/"
                                           "order-sourced token + missing containment + counterparty recipient); "
                                           "caller-own-asset / try-catch / pull-payment / allowlist / trusted-asset "
                                           "suppressed; admin-only downgraded",
            })
            candidates.append(c)

    # dedup to one candidate per (contract, shape), keeping the highest confidence
    rank = {"high": 3, "medium": 2, "low": 1}
    best: dict[str, dict] = {}
    for c in candidates:
        k = c["lens_id"]
        if k not in best or rank.get(c["confidence"], 0) > rank.get(best[k]["confidence"], 0):
            best[k] = c
    candidates = list(best.values())

    by_conf = Counter(c["confidence"] for c in candidates)
    report = {
        "lens": "hostile_token_settlement",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "manifest": str(man_path),
        "is_gate": False, "research_only": True, "routes_in_production": False,
        "routed_manifest_ids": [],          # research-only — never routes
        "raw_candidates": len(candidates),
        "by_confidence": dict(by_conf),
        "high": by_conf.get("high", 0), "medium": by_conf.get("medium", 0), "low": by_conf.get("low", 0),
        "candidates": candidates,
    }
    out = Path(args.out) if args.out else audit_path("output") / "hostile_token_settlement_audit.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))

    if not args.quiet:
        print(f"[hostile_token_settlement_audit] RESEARCH-ONLY (no routing) · candidates {len(candidates)} "
              f"· high {report['high']} medium {report['medium']} low {report['low']} · wrote {out}")
        for c in candidates:
            print(f"   • {c['contract']}.{c['function']} [{c['confidence']}] {c['cleanup_verb']} :: {c['transfer_primitive']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
