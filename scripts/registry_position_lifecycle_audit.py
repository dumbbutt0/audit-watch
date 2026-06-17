#!/usr/bin/env python3
"""
registry_position_lifecycle_audit.py — REGISTRY / POSITION-LIFECYCLE research lens (read-only,
is_gate:false, NOT wired). Anchored on NOYA H-23 (DolomiteConnector.transferBetweenAccounts omits the
registry.updateHoldingPosition its siblings perform) + H-18 (closeBorrowPosition removes unguarded).

Per contract: extract registry features for each function, run classify_contract. Reuses
sibling_function_parity_audit._function_body. Writes output/registry_position_lifecycle_audit.json.

RESEARCH-ONLY: NEVER mints findings, NEVER routes. routed_manifest_ids is always empty.

Usage: python scripts/registry_position_lifecycle_audit.py [--manifest <path>] [--no-source] [--quiet]
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
import registry_position_lifecycle_taxonomy as rpl
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
    ap.add_argument("--manifest")
    ap.add_argument("--no-source", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    man_path = Path(args.manifest) if args.manifest else audit_path("output") / "coverage_manifest.json"
    items = _load(man_path, "items")
    if not items:
        raise SystemExit(f"[registry_position_lifecycle_audit] no manifest items at {man_path}")
    use_source = not args.no_source

    fn_items = [it for it in items if it.get("kind") in ("function", "initializer")]
    in_scope_ids = {it["id"] for it in items if it.get("in_scope", True)}

    by_contract: dict[str, list] = defaultdict(list)
    item_by_key: dict[tuple, dict] = {}
    for it in fn_items:
        sp = it.get("source_span", {})
        body = _function_body(it.get("file", ""), sp.get("start_line"), use_source)
        feat = rpl.extract_registry_features(it.get("name", ""), it.get("signature", ""), body,
                                             visibility=it.get("visibility", ""),
                                             mutability=it.get("mutability", ""))
        by_contract[it.get("contract", "")].append(feat)
        item_by_key[(it.get("contract", ""), it.get("name", ""))] = it

    candidates = []
    for contract, feats in by_contract.items():
        for c in rpl.classify_contract(feats, contract):
            it = item_by_key.get((contract, c["function"]), {})
            sp = it.get("source_span", {})
            mid = it.get("id")
            c.update({
                "contract": contract, "file": it.get("file"),
                "file_line_refs": f"{it.get('file','')}:{sp.get('start_line','')}",
                "in_scope": mid in in_scope_ids if mid else False, "manifest_id": mid,
                "lens_id": f"{contract}.{c['function']}:{c['shape']}",
                "false_positive_controls": "lifecycle-verb omitter + shared subject proxy + non-view + "
                                           "external; amount-only verbs excluded; not Shape-C key-mismatch",
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
    by_shape = Counter(c["shape"] for c in candidates)

    report = {
        "lens": "registry_position_lifecycle",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "manifest": str(man_path),
        "is_gate": False, "research_only": True, "routes_in_production": False,
        "raw_candidates": len(candidates),
        "by_confidence": dict(by_conf), "by_shape": dict(by_shape),
        "high": by_conf.get("high", 0), "medium": by_conf.get("medium", 0), "low": by_conf.get("low", 0),
        "routed_manifest_ids": [],
        "candidates": candidates,
    }
    out = audit_path("output", "registry_position_lifecycle_audit.json")
    out.write_text(json.dumps(report, indent=2))

    if not args.quiet:
        print(f"[registry_position_lifecycle_audit] RESEARCH-ONLY (no routing) · candidates "
              f"{len(candidates)} · high {report['high']} medium {report['medium']} · "
              f"shapes {dict(by_shape)} · wrote {out}")
        for c in candidates:
            if c["confidence"] in ("high", "medium"):
                print(f"   • [{c['confidence']}] {c['contract']}.{c['function']} [{c['shape']}] "
                      f"subject={c.get('subject')} sibling={c.get('sibling_updater')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
