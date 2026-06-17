#!/usr/bin/env python3
"""
semantic_tvl_completeness_audit.py — SEMANTIC TVL-COMPLETENESS research prototype (read-only, is_gate=false,
NOT wired into routing). Contract-scoped: per connector, builds D (external value destinations its entrypoints
write) vs R (sources its TVL reader reads, + one level of same-contract helper resolution) and emits D\\R
candidates via semantic_tvl_completeness_taxonomy. Writes output/semantic_tvl_completeness_audit.json.

NEVER mints findings, NEVER routes. A `--research-route` flag exists for future experiments but is OFF by
default and is consumed by nothing (no gate reads this file).

Usage: python scripts/semantic_tvl_completeness_audit.py [--manifest <path>] [--no-source] [--quiet]
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
import semantic_tvl_completeness_taxonomy as stc  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
_FILE_CACHE: dict[str, list[str]] = {}
_BODY_MAX_LINES = 400
_DECREASE_REMOVE_RE = re.compile(r"(decrease|remove|unstake|withdraw|close)", re.I)
_INDIRECTION_RE = re.compile(r"delegatecall|\bproxy\b", re.I)
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest")
    ap.add_argument("--no-source", action="store_true")
    ap.add_argument("--research-route", action="store_true",
                    help="(experiment only) populate routed_manifest_ids; consumed by NOTHING. Default off.")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    man_path = Path(args.manifest) if args.manifest else audit_path("output") / "coverage_manifest.json"
    items = _load(man_path, "items")
    if not items:
        raise SystemExit(f"[semantic_tvl_completeness_audit] no manifest items at {man_path}")
    use_source = not args.no_source

    # group function items by contract; build name->body and the function lists
    by_contract: dict[str, list[dict]] = defaultdict(list)
    for it in items:
        if it.get("kind") in ("function", "initializer", "constructor") and it.get("contract"):
            by_contract[it["contract"]].append(it)

    candidates = []
    for contract, fns in by_contract.items():
        bodies = {}
        for it in fns:
            span = it.get("source_span", {})
            bodies[it["name"]] = _function_body(it.get("file", ""), span.get("start_line"), use_source)
        tvl_fns = [it for it in fns if stc.is_tvl_fn(it.get("name", "")) and bodies.get(it["name"])]
        if not tvl_fns:
            continue                                  # FP control: no TVL function in this connector

        # entrypoints = non-TVL functions; collect destinations (skip claim-only)
        dest_list = []
        for it in fns:
            nm = it["name"]
            if stc.is_tvl_fn(nm):
                continue
            body = bodies.get(nm, "")
            if not body or stc.is_claim_only(body):
                continue
            dest_list.extend(stc.parse_destinations(body))
        if not dest_list:
            continue

        has_decrease_remove = any(_DECREASE_REMOVE_RE.search(it["name"]) for it in fns)

        for tvl in tvl_fns:
            tbody = bodies.get(tvl["name"], "")
            # R = reads in the TVL body + one level of same-contract helper resolution
            reads = stc.parse_tvl_reads(tbody)
            for called in set(_LOCAL_CALL_RE.findall(tbody)):
                if called != tvl["name"] and called in bodies and not stc.is_tvl_fn(called):
                    reads.extend(stc.parse_tvl_reads(bodies[called]))
            indirection = bool(_INDIRECTION_RE.search(tbody))
            cands = stc.classify_group(contract, dest_list, reads, tvl["name"], indirection)
            cands += stc.classify_left_behind(contract, has_decrease_remove, dest_list, reads, tvl["name"])
            for c in cands:
                c["file"] = tvl.get("file")
                c["lens_id"] = f"{contract}:{tvl['name']}:{c['finding_shape']}"
                c["false_positive_controls"] = ("name-gated TVL fn; claim/approve/router/recipient excluded; "
                                                "helper-resolved reads; equivalent-source check")
                c["missing_context"] = ("registry/proxy/base-helper or tokenId/tick identity"
                                        if c["confidence"] == "needs_context" else "")
            candidates.extend(cands)

    # de-dup identical lens_ids
    seen, uniq = set(), []
    for c in candidates:
        if c["lens_id"] in seen:
            continue
        seen.add(c["lens_id"]); uniq.append(c)
    candidates = uniq

    # external_position_left_behind shares the same root as omitted_external_stake_balance — drop it for a
    # contract that already has the (more specific) omitted candidate, to avoid double-listing.
    omitted_contracts = {c["connector_contract"] for c in candidates
                         if c["finding_shape"] == "omitted_external_stake_balance"}
    candidates = [c for c in candidates if not (c["finding_shape"] == "external_position_left_behind"
                                                and c["connector_contract"] in omitted_contracts)]

    by_conf = Counter(c["confidence"] for c in candidates)
    report = {
        "lens": "semantic_tvl_completeness", "generated_at": datetime.now(timezone.utc).isoformat(),
        "manifest": str(man_path), "is_gate": False, "research_only": True, "routes_in_production": False,
        "raw_candidates": len(candidates),
        "by_shape": dict(Counter(c["finding_shape"] for c in candidates)),
        "by_confidence": dict(by_conf),
        "high": by_conf.get("high", 0), "medium": by_conf.get("medium", 0),
        "low": by_conf.get("low", 0), "needs_context": by_conf.get("needs_context", 0),
        # research-only: populated ONLY with --research-route, consumed by nothing
        "routed_manifest_ids": [] if not args.research_route else
            sorted({c["lens_id"] for c in candidates if c["confidence"] in stc.ROUTED_CONFIDENCE}),
        "candidates": candidates,
    }
    out = audit_path("output") / "semantic_tvl_completeness_audit.json"
    out.write_text(json.dumps(report, indent=2))

    if not args.quiet:
        print(f"[semantic_tvl_completeness_audit] RESEARCH-ONLY (no routing) · candidates {len(candidates)} "
              f"· high {report['high']} medium {report['medium']} needs_context {report['needs_context']} "
              f"· wrote {out}")
        for c in candidates:
            print(f"   • {c['connector_contract']}.{c['tvl_function']} [{c['finding_shape']}/{c['confidence']}] "
                  f"← {c['destination_call']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
