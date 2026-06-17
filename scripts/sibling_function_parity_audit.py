#!/usr/bin/env python3
"""
sibling_function_parity_audit.py — SIBLING-FUNCTION PARITY research lens (read-only, is_gate:false, NOT
wired into routing). Anchored on Blackhole M-04 (RewardsDistributor.claim vs claim_many: claim_many omits
the avm.getOriginalOwner recipient resolution).

For each contract it pairs sibling functions (name-stem groups + bounded behavioral pairing), brace-matches
both bodies (+1-level same-contract helper resolution), runs sibling_function_parity_taxonomy.classify_pair,
and emits candidates. Writes output/sibling_function_parity_audit.json.

RESEARCH-ONLY: NEVER mints findings, NEVER routes. routed_manifest_ids is always empty.

Usage: python scripts/sibling_function_parity_audit.py [--manifest <path>] [--no-source] [--quiet]
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
import sibling_function_parity_taxonomy as sfp

ROOT = Path(__file__).resolve().parent.parent
_FILE_CACHE: dict[str, list[str]] = {}
_BODY_MAX_LINES = 400
_LOCAL_CALL_RE = re.compile(r"(?<![.\w])([A-Za-z_]\w*)\s*\(")
_FULL_PAIR_LIMIT = 250  # contracts larger than this: pair within name-stem groups only (cost bound)


def _load(path: Path, key: str):
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
    ap.add_argument("--manifest", help="coverage_manifest.json (default: active audit output)")
    ap.add_argument("--no-source", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    man_path = Path(args.manifest) if args.manifest else audit_path("output") / "coverage_manifest.json"
    items = _load(man_path, "items")
    if not items:
        raise SystemExit(f"[sibling_function_parity_audit] no manifest items at {man_path}")
    use_source = not args.no_source

    fn_items = [it for it in items if it.get("kind") in ("function", "initializer")
                and it.get("mutability") not in ("view", "pure")]
    in_scope_ids = {it["id"] for it in items if it.get("in_scope", True)}

    by_contract: dict[str, list[dict]] = defaultdict(list)
    bodies: dict[str, dict[str, str]] = defaultdict(dict)
    for it in fn_items:
        sp = it.get("source_span", {})
        b = _function_body(it.get("file", ""), sp.get("start_line"), use_source)
        bodies[it.get("contract", "")][it.get("name", "")] = b
        by_contract[it.get("contract", "")].append(it)

    def features_for(it):
        c, name = it.get("contract", ""), it.get("name", "")
        body = bodies[c].get(name, "")
        # own-body features (pre-resolution) — used for forwarder/wrapper suppression
        own = sfp.extract_features(name, it.get("signature", ""), it.get("modifiers"), body,
                                   visibility=it.get("visibility", ""))
        # +1-level same-contract helper resolution (pull in shared helpers like _validate())
        resolved = body
        for called in set(_LOCAL_CALL_RE.findall(body)):
            if called != name and called in bodies[c]:
                resolved += "\n" + bodies[c][called]
        feat = sfp.extract_features(name, it.get("signature", ""), it.get("modifiers"), resolved,
                                    visibility=it.get("visibility", ""))
        feat["own_calls"] = own["calls"]
        feat["own_ncalls"] = own["_ncalls"]
        return feat

    candidates = []
    for contract, fns in by_contract.items():
        if len(fns) < 2:
            continue
        feats = {it.get("name", ""): features_for(it) for it in fns}
        item_by_name = {it.get("name", ""): it for it in fns}
        # build pair list: name-stem groups always; full pairwise only for small contracts
        pairs = set()
        stem_groups = defaultdict(list)
        for it in fns:
            nm = it.get("name", "")
            stem_groups[("s", feats[nm]["stem"])].append(nm)
            stem_groups[("c", feats[nm]["core"])].append(nm)
        for names in stem_groups.values():
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    a, b = names[i], names[j]
                    if a != b:
                        pairs.add(tuple(sorted((a, b))))
        if len(fns) <= _FULL_PAIR_LIMIT:
            names = [it.get("name", "") for it in fns]
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    pairs.add((names[i], names[j]))

        for na, nb in pairs:
            for c in sfp.classify_pair(feats[na], feats[nb]):
                weak_it = item_by_name.get(c["weak"], {})
                sp = weak_it.get("source_span", {})
                mid = weak_it.get("id")
                c.update({
                    "contract": contract,
                    "sibling_pair": [c["strong"], c["weak"]],
                    "function": c["weak"],
                    "file": weak_it.get("file"),
                    "file_line_refs": f"{weak_it.get('file','')}:{sp.get('start_line','')}",
                    "in_scope": mid in in_scope_ids if mid else False,
                    "manifest_id": mid,
                    "lens_id": f"{contract}:{c['strong']}~{c['weak']}:{c['parity_type']}:{c['missing_component']}",
                    "false_positive_controls": "two-signal (sibling kinship + controlled-vocab asymmetry); "
                                               "wrapper/admin/view/event-cast/observability suppressed; +1 helper resolved",
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
        "lens": "sibling_function_parity",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "manifest": str(man_path),
        "is_gate": False, "research_only": True, "routes_in_production": False,
        "raw_candidates": len(candidates),
        "by_confidence": dict(by_conf),
        "by_parity_type": dict(by_type),
        "high": by_conf.get("high", 0), "medium": by_conf.get("medium", 0), "low": by_conf.get("low", 0),
        "routed_manifest_ids": [],
        "candidates": candidates,
    }
    out = audit_path("output", "sibling_function_parity_audit.json")
    out.write_text(json.dumps(report, indent=2))

    if not args.quiet:
        print(f"[sibling_function_parity_audit] RESEARCH-ONLY (no routing) · candidates {len(candidates)} "
              f"· high {report['high']} medium {report['medium']} · types {dict(by_type)} · wrote {out}")
        for c in candidates:
            if c["confidence"] == "high":
                print(f"   • {c['contract']}.{c['strong']}~{c['weak']} [{c['parity_type']}] "
                      f"missing={c['missing_component']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
