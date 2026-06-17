#!/usr/bin/env python3
"""
value_flow_parity_audit.py — VALUE-FLOW PARITY research lens (read-only, is_gate:false, NOT wired).
Anchored on Size M-02 (validateSellCreditMarket guards `params.amount < minimumCreditBorrowAToken`).

Per function: runs classify_intra (identity check-vs-use / threshold-name value mismatch / net-gross).
Per contract: pairs validate*/execute* siblings (same _core) and runs classify_validate_execute_pair.
Writes output/value_flow_parity_audit.json.

RESEARCH-ONLY: NEVER mints findings, NEVER routes. routed_manifest_ids is always empty.

Usage: python scripts/value_flow_parity_audit.py [--manifest <path>] [--no-source] [--quiet]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path
import value_flow_parity_taxonomy as vfp
import sibling_function_parity_taxonomy as sfp
from sibling_function_parity_audit import _function_body

ROOT = Path(__file__).resolve().parent.parent


def _load(path: Path, key: str):
    try:
        d = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return []
    return d.get(key, []) if isinstance(d, dict) else d


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", help="coverage_manifest.json (default: active audit output)")
    ap.add_argument("--no-source", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    man_path = Path(args.manifest) if args.manifest else audit_path("output") / "coverage_manifest.json"
    items = _load(man_path, "items")
    if not items:
        raise SystemExit(f"[value_flow_parity_audit] no manifest items at {man_path}")
    use_source = not args.no_source

    fn_items = [it for it in items if it.get("kind") in ("function", "initializer")]
    in_scope_ids = {it["id"] for it in items if it.get("in_scope", True)}

    candidates = []
    by_contract = defaultdict(list)

    for it in fn_items:
        sp = it.get("source_span", {})
        body = _function_body(it.get("file", ""), sp.get("start_line"), use_source)
        name, contract, mid = it.get("name", ""), it.get("contract", ""), it.get("id")
        for c in vfp.classify_intra(name, it.get("signature", ""), body):
            c.update({"contract": contract, "function": name, "file": it.get("file"),
                      "file_line_refs": f"{it.get('file','')}:{sp.get('start_line','')}",
                      "in_scope": mid in in_scope_ids if mid else False, "manifest_id": mid,
                      "lens_id": f"{contract}.{name}:{c['shape']}:{c['guard_value']}->{c['effect_value']}",
                      "false_positive_controls": "curated alias vocab + two-context split; not asset-source-family"})
            candidates.append(c)
        # collect for validate/execute pairing
        feat = sfp.extract_features(name, it.get("signature", ""), it.get("modifiers"), body,
                                    visibility=it.get("visibility", ""))
        by_contract[contract].append({
            "name": name, "guard_idents": vfp.guard_idents(body),
            "effect_operands": vfp.effect_operands(body),
            "calls_lower": {c.lower() for c in feat["calls"]}, "_item": it})

    # ---- validate/execute sibling pairing (shape 2b) ----
    for contract, fns in by_contract.items():
        for i in range(len(fns)):
            for j in range(i + 1, len(fns)):
                for c in vfp.classify_validate_execute_pair(fns[i], fns[j]):
                    weak_it = next((f["_item"] for f in (fns[i], fns[j]) if f["name"] == c["weak"]), {})
                    sp = weak_it.get("source_span", {})
                    mid = weak_it.get("id")
                    c.update({"contract": contract, "function": c["weak"], "file": weak_it.get("file"),
                              "sibling_pair": [f"{contract}.{c['strong']}", f"{contract}.{c['weak']}"],
                              "file_line_refs": f"{weak_it.get('file','')}:{sp.get('start_line','')}",
                              "in_scope": mid in in_scope_ids if mid else False, "manifest_id": mid,
                              "lens_id": f"{contract}.{c['strong']}~{c['weak']}:{c['shape']}:"
                                         f"{c['guard_value']}->{c['effect_value']}",
                              "false_positive_controls": "validate/execute core-sibling + value alias vocab"})
                    candidates.append(c)

    seen, uniq = set(), []
    for c in candidates:
        if c["lens_id"] in seen:
            continue
        seen.add(c["lens_id"])
        uniq.append(c)
    candidates = uniq
    by_conf = Counter(c["confidence"] for c in candidates)
    by_shape = Counter(c["shape"] for c in candidates)

    report = {
        "lens": "value_flow_parity",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "manifest": str(man_path),
        "is_gate": False, "research_only": True, "routes_in_production": False,
        "raw_candidates": len(candidates),
        "by_confidence": dict(by_conf), "by_shape": dict(by_shape),
        "high": by_conf.get("high", 0), "medium": by_conf.get("medium", 0), "low": by_conf.get("low", 0),
        "routed_manifest_ids": [],
        "candidates": candidates,
    }
    out = audit_path("output", "value_flow_parity_audit.json")
    out.write_text(json.dumps(report, indent=2))

    if not args.quiet:
        print(f"[value_flow_parity_audit] RESEARCH-ONLY (no routing) · candidates {len(candidates)} "
              f"· high {report['high']} medium {report['medium']} low {report['low']} · "
              f"shapes {dict(by_shape)} · wrote {out}")
        for c in candidates:
            if c["confidence"] in ("high", "medium"):
                print(f"   • [{c['confidence']}] {c['contract']}.{c['function']} [{c['shape']}] "
                      f"{c['guard_value']} -> {c['effect_value']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
