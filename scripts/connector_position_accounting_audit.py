#!/usr/bin/env python3
"""
connector_position_accounting_audit.py — CONNECTOR / TVL / POSITION-ACCOUNTING recall lens (read-time,
advisory, is_gate=false). Narrow first slice proven by the NOYA 2024-04 eval — three name-gated shapes:
  - external_reader_aggregate  (H-11 SNX, H-19 MorphoBlue): TVL aggregate of external-reader terms.
  - position_tvl_product_div   (H-13 Balancer): PositionTVL product/division miscalc.
  - registry_key_mismatch      (H-12 Registry.updateHoldingPosition): msg.sender vs calculatorConnector key.

Classification lives in connector_position_accounting_taxonomy.classify() (pure, tested). This reads the
coverage manifest + each function body from source (brace-matched), the dispositions (status), and
arithmetic_conservation_audit.json (to DE-DUP — items arithmetic already routes are recorded as
context_only so this lens reports only net-new recovery). Never writes dispositions or findings.
Routing is done by advisory_escalation_gate.py reading `routed_manifest_ids` (high+medium), strict full-audit.

Usage: python scripts/connector_position_accounting_audit.py [--manifest <path>] [--no-source] [--quiet]
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
import connector_position_accounting_taxonomy as cpa  # noqa: E402

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
    """Extract exactly the function body by brace-matching from `start` (copied from
    arithmetic_conservation_audit — avoids the fixed-window neighbour bleed)."""
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
    while j < min(n, i + 8) and "{" not in lines[j]:
        j += 1
    if j >= min(n, i + 8) or "{" not in lines[j]:
        return ""
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


def _arithmetic_routed_ids() -> set:
    d = _load(audit_path("output") / "arithmetic_conservation_audit.json", "routed_manifest_ids")
    return set(d)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", help="manifest path (default: live coverage_manifest.json)")
    ap.add_argument("--no-source", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    man_path = Path(args.manifest) if args.manifest else audit_path("output") / "coverage_manifest.json"
    items = _load(man_path, "items")
    if not items:
        raise SystemExit(f"[connector_position_accounting_audit] no manifest items at {man_path}")
    use_source = not args.no_source

    in_scope_ids = {it["id"] for it in items if it.get("in_scope", True)}
    disp = {d["manifest_id"]: d for d in _load(audit_path("output") / "coverage_dispositions.json", "dispositions")}
    arith_ids = _arithmetic_routed_ids()

    detected = []
    for it in items:
        if it.get("kind") not in ("function", "initializer", "constructor"):
            continue
        span = it.get("source_span", {})
        snip = _function_body(it.get("file", ""), span.get("start_line"), use_source)
        cls = cpa.classify(it.get("name", ""), it.get("signature", ""), it.get("file", ""),
                          it.get("contract", ""), snippet=snip, tags=it.get("tags"))
        if not cls.get("sensitive"):
            continue
        mid = it.get("id")
        deduped = mid in arith_ids   # arithmetic_conservation already routes it → report as context-only
        d = disp.get(mid, {})
        detected.append({
            "manifest_id": mid, "contract": it.get("contract"), "name": it.get("name"),
            "file": it.get("file"), "shape": cls["shape"], "signals": cls["signals"],
            "confidence": cls["confidence"], "terms": cls["terms"], "reason": cls["reason"],
            "in_scope": mid in in_scope_ids, "coverage_status": d.get("status", "unassigned"),
            "dedup_arithmetic_conservation": deduped,
        })

    routed_ids = sorted({x["manifest_id"] for x in detected
                         if x["confidence"] in cpa.ROUTED_CONFIDENCE and x["in_scope"]
                         and not x["dedup_arithmetic_conservation"]})
    context_only = sorted({x["manifest_id"] for x in detected if x["manifest_id"] not in set(routed_ids)})
    n_in_scope = max(1, len(in_scope_ids))
    route_rate = round(len(routed_ids) / n_in_scope, 4)

    ts = datetime.now(timezone.utc).isoformat()
    report = {
        "lens": "connector_position_accounting", "generated_at": ts, "manifest": str(man_path), "is_gate": False,
        "total_sensitive": len(detected),
        "by_shape": dict(Counter(x["shape"] for x in detected)),
        "by_confidence": dict(Counter(x["confidence"] for x in detected)),
        "dedup_arithmetic_conservation": sum(1 for x in detected if x["dedup_arithmetic_conservation"]),
        "routed_manifest_ids": routed_ids,
        "route_rate": route_rate,
        "context_only": context_only,
        "detected": detected,
    }
    out = audit_path("output") / "connector_position_accounting_audit.json"
    out.write_text(json.dumps(report, indent=2))

    md = [f"# connector_position_accounting lens\n",
          f"Sensitive: **{len(detected)}** · routed (net-new high/medium): **{len(routed_ids)}** · "
          f"route_rate **{route_rate}** · context-only **{len(context_only)}** · "
          f"arithmetic de-dup **{report['dedup_arithmetic_conservation']}**\n",
          f"by shape: {report['by_shape']} · by confidence: {report['by_confidence']}\n"]
    for x in detected:
        if x["manifest_id"] in routed_ids:
            md.append(f"- **{x['contract']}.{x['name']}** [{x['shape']}/{x['confidence']}] — {x['reason']}")
    (audit_path("output") / "connector_position_accounting_audit.md").write_text("\n".join(md))

    if not args.quiet:
        print(f"[connector_position_accounting_audit] {len(detected)} sensitive · routed {len(routed_ids)} "
              f"(rate {route_rate}) · context-only {len(context_only)} · "
              f"dedup {report['dedup_arithmetic_conservation']} · wrote {out}")
        for x in detected:
            if x["manifest_id"] in routed_ids:
                print(f"   → {x['contract']}.{x['name']} ({x['shape']}, {x['confidence']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
