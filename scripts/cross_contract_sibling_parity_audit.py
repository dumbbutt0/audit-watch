#!/usr/bin/env python3
"""
cross_contract_sibling_parity_audit.py — CROSS-CONTRACT sibling parity research lens (read-only,
is_gate:false, NOT wired). Anchored on Size Credit M-06 (BuyCreditMarket.validateBuyCreditMarket guards
`!creditPosition.forSale`; SellCreditMarket.validateSellCreditMarket omits it on the same creditPosition).

Pairs sibling functions ACROSS contracts, bucketed by (module dir x action-verb x state-struct) so
pairing is bounded and cross-sibling-gated. Reuses sibling_function_parity_audit._function_body and the
Tier-1A taxonomy helpers. Writes output/cross_contract_sibling_parity_audit.json.

RESEARCH-ONLY: NEVER mints findings, NEVER routes. routed_manifest_ids is always empty.

Usage: python scripts/cross_contract_sibling_parity_audit.py [--manifest <path>] [--no-source] [--quiet]
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
from audit_context import audit_path
import cross_contract_sibling_parity_taxonomy as ccs
from sibling_function_parity_audit import _function_body, _LOCAL_CALL_RE  # reuse body extractor

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
        raise SystemExit(f"[cross_contract_sibling_parity_audit] no manifest items at {man_path}")
    use_source = not args.no_source

    # include view/pure: validator functions are the target. keep only function-like items.
    fn_items = [it for it in items if it.get("kind") in ("function", "initializer")]
    in_scope_ids = {it["id"] for it in items if it.get("in_scope", True)}

    # bodies per contract for +1 helper resolution
    bodies: dict[str, dict[str, str]] = defaultdict(dict)
    for it in fn_items:
        sp = it.get("source_span", {})
        bodies[it.get("contract", "")][it.get("name", "")] = _function_body(
            it.get("file", ""), sp.get("start_line"), use_source)

    def features_for(it):
        c, name = it.get("contract", ""), it.get("name", "")
        body = bodies[c].get(name, "")
        own = ccs.sfp.extract_features(name, it.get("signature", ""), it.get("modifiers"), body,
                                       visibility=it.get("visibility", ""))
        resolved = body
        for called in set(_LOCAL_CALL_RE.findall(body)):
            if called != name and called in bodies[c]:
                resolved += "\n" + bodies[c][called]
        feat = ccs.extract_cross_features(name, it.get("signature", ""), it.get("modifiers"), resolved,
                                          visibility=it.get("visibility", ""), file=it.get("file", ""),
                                          contract=c)
        feat["own_calls"] = own["calls"]
        feat["own_ncalls"] = own["_ncalls"]
        feat["_item"] = it
        return feat

    feats = [features_for(it) for it in fn_items]
    # bucket by (module_dir, verb, state_struct); only verb-bearing, state-struct-bearing items pair
    buckets: dict[tuple, list] = defaultdict(list)
    for f in feats:
        if f["verb"] and f["state_struct"]:
            buckets[(f["module_dir"], f["verb"], f["state_struct"])].append(f)

    candidates = []
    for key, group in buckets.items():
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                fa, fb = group[i], group[j]
                if fa["contract"] == fb["contract"]:
                    continue  # cross-CONTRACT only
                for c in ccs.classify_cross_pair(fa, fb):
                    weak_it = (fa if c["weak_contract"] == fa["contract"] else fb)["_item"]
                    sp = weak_it.get("source_span", {})
                    mid = weak_it.get("id")
                    c.update({
                        "sibling_pair": [f"{c['strong_contract']}.{c['strong']}",
                                         f"{c['weak_contract']}.{c['weak']}"],
                        "function": c["weak"], "contract": c["weak_contract"],
                        "file": weak_it.get("file"),
                        "file_line_refs": f"{weak_it.get('file','')}:{sp.get('start_line','')}",
                        "in_scope": mid in in_scope_ids if mid else False, "manifest_id": mid,
                        "lens_id": f"{c['strong_contract']}.{c['strong']}~{c['weak_contract']}.{c['weak']}"
                                   f":{c['parity_type']}:{c['missing_component']}",
                        "false_positive_controls": "multi-gate cross-sibling (same verb+module+state-struct"
                                                   "+>=2 shared calls); wrapper/admin/external-weak/exclude suppressed",
                    })
                    candidates.append(c)

    seen, uniq = set(), []
    for c in candidates:
        if c["lens_id"] in seen:
            continue
        seen.add(c["lens_id"])
        uniq.append(c)
    candidates = uniq
    by_conf = Counter(c["confidence"] for c in candidates)
    by_type = Counter(c["parity_type"] for c in candidates)

    report = {
        "lens": "cross_contract_sibling_parity",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "manifest": str(man_path),
        "is_gate": False, "research_only": True, "routes_in_production": False,
        "raw_candidates": len(candidates),
        "by_confidence": dict(by_conf), "by_parity_type": dict(by_type),
        "high": by_conf.get("high", 0), "medium": by_conf.get("medium", 0), "low": by_conf.get("low", 0),
        "routed_manifest_ids": [],
        "candidates": candidates,
    }
    out = audit_path("output", "cross_contract_sibling_parity_audit.json")
    out.write_text(json.dumps(report, indent=2))

    if not args.quiet:
        print(f"[cross_contract_sibling_parity_audit] RESEARCH-ONLY (no routing) · candidates "
              f"{len(candidates)} · high {report['high']} medium {report['medium']} · "
              f"types {dict(by_type)} · wrote {out}")
        for c in candidates:
            if c["confidence"] in ("high", "medium"):
                print(f"   • [{c['confidence']}] {c['strong_contract']}.{c['strong']}~"
                      f"{c['weak_contract']}.{c['weak']} [{c['parity_type']}] missing={c['missing_component']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
