#!/usr/bin/env python3
"""
arithmetic_conservation_audit.py — ARITHMETIC-CONSERVATION recall lens (read-time, advisory, is_gate=false).

Detects two conservation shapes the attack-surface scorer under-weights (so they score low and get
thin-cleared), and routes its OWN high/medium hits to a deep pass via advisory_escalation_gate:
  - shape "supply_aggregate"   : a multi-term supply/balance aggregate with balanceOf/totalSupply or a
                                 supply-named term  -> double-count risk (Blackhole M-01 calculate_rebase).
  - shape "invariant_rounding" : a product/invariant helper with integer division -> floor-to-zero risk
                                 (Blackhole M-06 Pair._k). Looser; overlaps math_estimator -> de-duped here.

Classification logic lives in arithmetic_conservation_taxonomy.classify() (pure, tested). This script reads
the coverage manifest + each function body from source (manifest stores only the signature) + the coverage
dispositions (for status) + math_estimator_audit.json (for shape-2 de-dup). It NEVER writes dispositions or
findings. Writes output/arithmetic_conservation_audit.json (+ .md). Routing is done by
advisory_escalation_gate.py reading `routed_manifest_ids` (high+medium), strict full-audit only.

Usage: python scripts/arithmetic_conservation_audit.py [--manifest <path>] [--no-source] [--quiet]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
import arithmetic_conservation_taxonomy as ac  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
_FILE_CACHE: dict[str, list[str]] = {}
# safety cap on body length (lines) when brace-matching, so a malformed/unbalanced source can't run away.
_BODY_MAX_LINES = 400


def _load(path: Path, key: str) -> list:
    try:
        d = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return []
    return d.get(key, []) if isinstance(d, dict) else d


def _function_body(file_rel, start, use_source) -> str:
    """Extract EXACTLY the function body by brace-matching from `start` — not a fixed lookahead window
    (a fixed window bleeds into the next function and creates FPs: a one-line setter + 25 lines pulls in a
    neighbour's balanceOf+aggregate). Returns "" for declaration-only items (no `{` near the start)."""
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
    # find the opening brace within a few lines (multi-line signatures)
    j = i
    while j < min(n, i + 8) and "{" not in lines[j]:
        j += 1
    if j >= min(n, i + 8) or "{" not in lines[j]:
        return ""  # no body (interface/abstract decl)
    depth = 0
    out = []
    started = False
    for k in range(j, min(n, j + _BODY_MAX_LINES)):
        line = lines[k]
        out.append(line)
        depth += line.count("{") - line.count("}")
        if "{" in line:
            started = True
        if started and depth <= 0:
            break
    return "\n".join(out)[:8000]


def _math_estimator_ids() -> set:
    """manifest_ids already flagged by math_estimator (for shape-2 de-dup)."""
    det = _load(audit_path("output") / "math_estimator_audit.json", "detected")
    return {d.get("manifest_id") for d in det if isinstance(d, dict) and d.get("manifest_id")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", help="manifest path (default: live coverage_manifest.json)")
    ap.add_argument("--no-source", action="store_true", help="do not read bodies from source")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    man_path = Path(args.manifest) if args.manifest else audit_path("output") / "coverage_manifest.json"
    items = _load(man_path, "items")
    if not items:
        raise SystemExit(f"[arithmetic_conservation_audit] no manifest items at {man_path}")
    use_source = not args.no_source

    in_scope_ids = {it["id"] for it in items if it.get("in_scope", True)}
    disp = {d["manifest_id"]: d for d in _load(audit_path("output") / "coverage_dispositions.json", "dispositions")}
    me_ids = _math_estimator_ids()

    detected = []
    for it in items:
        if it.get("kind") not in ("function", "initializer", "constructor"):
            continue
        span = it.get("source_span", {})
        snip = _function_body(it.get("file", ""), span.get("start_line"), use_source)
        cls = ac.classify(it.get("name", ""), it.get("signature", ""), it.get("file", ""),
                          it.get("contract", ""), snippet=snip, tags=it.get("tags"))
        if not cls.get("sensitive"):
            continue
        mid = it.get("id")
        confidence = cls["confidence"]
        deduped = False
        # shape-2 de-dup: math_estimator already owns generic product/division math
        if cls["shape"] == "invariant_rounding" and mid in me_ids:
            deduped = True
        d = disp.get(mid, {})
        detected.append({
            "manifest_id": mid, "contract": it.get("contract"), "name": it.get("name"),
            "file": it.get("file"), "shape": cls["shape"], "signals": cls["signals"],
            "confidence": confidence, "terms": cls["terms"], "reason": cls["reason"],
            "in_scope": mid in in_scope_ids,
            "coverage_status": d.get("status", "unassigned"),
            "dedup_math_estimator": deduped,
        })

    # routed = high/medium, in-scope, not deduped, not already terminal
    routed_ids = sorted({x["manifest_id"] for x in detected
                         if x["confidence"] in ac.ROUTED_CONFIDENCE and x["in_scope"]
                         and not x["dedup_math_estimator"]})
    context_only = sorted({x["manifest_id"] for x in detected if x["manifest_id"] not in set(routed_ids)})
    n_in_scope = max(1, len(in_scope_ids))
    route_rate = round(len(routed_ids) / n_in_scope, 4)

    ts = datetime.now(timezone.utc).isoformat()
    report = {
        "lens": "arithmetic_conservation", "generated_at": ts, "manifest": str(man_path), "is_gate": False,
        "total_sensitive": len(detected),
        "by_shape": dict(Counter(x["shape"] for x in detected)),
        "by_confidence": dict(Counter(x["confidence"] for x in detected)),
        "dedup_math_estimator": sum(1 for x in detected if x["dedup_math_estimator"]),
        "routed_manifest_ids": routed_ids,
        "route_rate": route_rate,
        "context_only": context_only,
        "detected": detected,
    }
    out = audit_path("output") / "arithmetic_conservation_audit.json"
    out.write_text(json.dumps(report, indent=2))

    md = [f"# arithmetic_conservation lens\n",
          f"Sensitive: **{len(detected)}** · routed (high/medium): **{len(routed_ids)}** · "
          f"route_rate **{route_rate}** · context-only **{len(context_only)}** · "
          f"math_estimator de-dup **{report['dedup_math_estimator']}**\n",
          f"by shape: {report['by_shape']} · by confidence: {report['by_confidence']}\n"]
    for x in detected:
        if x["manifest_id"] in routed_ids:
            md.append(f"- **{x['contract']}.{x['name']}** [{x['shape']}/{x['confidence']}] — {x['reason']}")
    (audit_path("output") / "arithmetic_conservation_audit.md").write_text("\n".join(md))

    if not args.quiet:
        print(f"[arithmetic_conservation_audit] {len(detected)} sensitive · routed {len(routed_ids)} "
              f"(rate {route_rate}) · context-only {len(context_only)} · "
              f"dedup {report['dedup_math_estimator']} · wrote {out}")
        for x in detected:
            if x["manifest_id"] in routed_ids:
                print(f"   → {x['contract']}.{x['name']} ({x['shape']}, {x['confidence']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
