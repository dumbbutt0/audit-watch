#!/usr/bin/env python3
"""
getter_state_audit.py — Getter-vs-state reconciliation detector + review-packet report.

Applies the getter_state_patterns.json taxonomy (via getter_state_taxonomy.classify) to the coverage
manifest. The signal lives in function BODIES, so this detector READS THE SOURCE SNIPPET around each
manifest source_span and classifies on it. It also builds a lightweight CONSUMER cross-reference (which
view/getter names are called inside state-changing function bodies) to power `view_used_by_state_path`.
Cross-references dispositions (finding / cleared / deferred). Read-time over the (frozen) manifest — no
rebuild — so eval3 integrity is preserved. Pure report; NOT a gate.

Headline: "Previously cleared but high-risk getter/state reconciliation items" — a getter cleared as
"view-only, no fund-flow" (e.g. SeasonGettersFacet.totalDeltaB, #30) can still return a wrong value a
state path trusts.

Reads:  output/coverage_manifest.json (or --manifest), config/getter_state_patterns.json,
        output/coverage_dispositions.json (optional), + source files for snippets.
Writes: output/getter_state_audit.{json,md}

Usage: python scripts/getter_state_audit.py [--manifest <path>] [--no-source]
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
import getter_state_taxonomy as gs  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

# Honest mapping of category -> residual eval miss it plausibly recovers. All six targets
# (#30/#99/#279/#307/#309/#461) are enumerated in the frozen manifest and tagged by this lens.
CATEGORY_TO_MISS = {
    "wrong_return_field": ["#30 SeasonGettersFacet.totalDeltaB sums wrong well set"],
    "consumer_assumption_mismatch": ["#30-adjacent consumer trusts totalDeltaB scope"],
    "wrong_state_variable": ["#99 TractorFacet counter getter returns wrong field"],
    "stale_getter": ["#99-adjacent stale/wrong counter getter"],
    "branch_mismatch": ["#307 multiple sunrise (seasonTime cadence branch)", "#279-adjacent tractor refund branch"],
    "default_value_mismatch": ["#307-adjacent seasonTime default branches"],
    "view_used_by_state_path": ["#307/#30 view consumed by state path"],
    "abi_encoding_mismatch": ["#309 AdvancedPipeCall vs AdvancedFarmCall decode", "#279 tractor abi.decode(AdvancedFarmCall[])"],
    "struct_field_mismatch": ["#309 pipe/farm struct-field divergence"],
    "calldata_offset_mismatch": ["#309-adjacent clipboard/paste calldata offsets"],
    "sorting_or_ordering_bug": ["#461 LibFlood.quickSort well ordering before flood allocation"],
}

_FILE_CACHE: dict[str, list[str]] = {}


def _lines(file_rel: str) -> list[str]:
    if file_rel not in _FILE_CACHE:
        try:
            _FILE_CACHE[file_rel] = (ROOT / file_rel).read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            _FILE_CACHE[file_rel] = []
    return _FILE_CACHE[file_rel]


def _snippet(file_rel: str, start: int, end: int, use_source: bool) -> str:
    if not use_source or not file_rel or not start:
        return ""
    lines = _lines(file_rel)
    if not lines:
        return ""
    a = max(0, (start or 1) - 1)
    b = min(len(lines), (end or start or 1) + 6)   # small lookahead to capture the return/body
    return "\n".join(lines[a:b])[:4000]


def _load(path: Path, key: str):
    if not path.exists():
        return [] if key else {}
    try:
        d = json.loads(path.read_text())
        return d.get(key, []) if key else d
    except (OSError, json.JSONDecodeError):
        return [] if key else {}


def _build_consumer_set(items: list[dict], use_source: bool) -> set[str]:
    """Names called inside state-changing (nonpayable/payable) function bodies."""
    blob_parts = []
    for it in items:
        if it.get("kind") not in ("function", "initializer"):
            continue
        if (it.get("mutability") or "") in ("view", "pure"):
            continue
        span = it.get("source_span", {})
        blob_parts.append(_snippet(it.get("file", ""), span.get("start_line"), span.get("end_line"), use_source))
    blob = "\n".join(blob_parts)
    return set(re.findall(r"\b([A-Za-z_]\w+)\s*\(", blob))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", help="manifest path (default: live coverage_manifest.json)")
    ap.add_argument("--no-source", action="store_true", help="classify on signature only (no body snippet)")
    args = ap.parse_args()

    man_path = Path(args.manifest) if args.manifest else audit_path("output") / "coverage_manifest.json"
    items = _load(man_path, "items")
    if not items:
        raise SystemExit(f"[getter_state_audit] no manifest items at {man_path}")
    tax = gs.load_taxonomy()
    disp = {d["manifest_id"]: d for d in _load(audit_path("output") / "coverage_dispositions.json", "dispositions")}
    use_source = not args.no_source
    consumers = _build_consumer_set(items, use_source)

    detected = []
    for it in items:
        if it.get("kind") not in ("function", "initializer"):
            continue
        name = it.get("name", "")
        span = it.get("source_span", {})
        snip = _snippet(it.get("file", ""), span.get("start_line"), span.get("end_line"), use_source)
        consumed = name in consumers
        cls = gs.classify(name, it.get("signature", ""), it.get("file", ""), it.get("contract", ""),
                          snippet=snip, mutability=it.get("mutability", ""), tags=it.get("tags"),
                          consumed_by_state=consumed, taxonomy=tax)
        if not cls.get("getter_state_sensitive"):
            continue
        d = disp.get(it["id"], {})
        status = d.get("status")
        coverage = ("covered_by_finding" if status == "finding"
                    else "examined_but_cleared" if status == "cleared"
                    else "deferred" if status == "deferred" else "uncovered")
        detected.append({
            "manifest_id": it["id"], "name": name, "contract": it.get("contract"),
            "file": it.get("file"), "line": span.get("start_line"),
            "mutability": it.get("mutability"), "category": cls["category"],
            "risk_tags": cls["risk_tags"], "high_risk": gs.is_high_risk(cls, tax),
            "severity_ceiling_hint": cls["severity_ceiling_hint"], "in_scope": it.get("in_scope", True),
            "return_shape": cls["return_shape"], "state_reads": cls["state_reads"],
            "consumer_hint": cls["consumer_hint"], "matched_on": cls["matched_on"],
            "features": cls["features"], "coverage": coverage, "disposition_status": status,
            "finding_refs": d.get("finding_refs", []), "clear_reason": d.get("clear_reason"),
            "signature": (it.get("signature") or "")[:200],
        })

    by_category = Counter(x["category"] for x in detected)
    high_risk = [x for x in detected if x["high_risk"]]
    prev_cleared_hr = [x for x in detected if x["high_risk"] and x["coverage"] == "examined_but_cleared"]
    finding_linked = [x["manifest_id"] for x in detected if x["coverage"] == "covered_by_finding"]
    examined_cleared = [x["manifest_id"] for x in detected if x["coverage"] == "examined_but_cleared"]
    uncovered = [x["manifest_id"] for x in detected if x["coverage"] == "uncovered"]
    re_review = [x for x in detected if x["high_risk"] and x["coverage"] != "covered_by_finding"]

    by_cat_items = defaultdict(list)
    for x in re_review:
        by_cat_items[x["category"]].append(x)
    packets = []
    for i, (cat, xs) in enumerate(sorted(by_cat_items.items()), 1):
        meta = tax.get("categories", {}).get(cat, {})
        packets.append({
            "packet_id": f"GS-{i:02d}", "label": f"getter/state: {cat}", "category": cat,
            "suggested_specialist": "behavioral_state_analysis",
            "severity_ceiling_hint": meta.get("severity_ceiling_hint"),
            "item_ids": sorted(x["manifest_id"] for x in xs),
            "files": sorted({x["file"] for x in xs if x["file"]}),
            "review_prompt": ("Reconcile each getter's return value against the state it claims to report "
                              "(prompts/getter_state_review.md). " + (meta.get("review_hint") or "")),
        })

    likely = []
    for cat in by_category:
        likely += CATEGORY_TO_MISS.get(cat, [])
    likely = sorted(set(likely))

    ts = datetime.now(timezone.utc).isoformat()
    report = {
        "generated_at": ts, "manifest": str(man_path), "is_gate": False, "source_snippets": use_source,
        "lens": "getter_state_reconciliation",
        "total_getter_state_sensitive": len(detected),
        "by_category": dict(by_category), "high_risk_count": len(high_risk),
        "re_review_candidates": len(re_review),
        "previously_cleared_high_risk": prev_cleared_hr,
        "covered_by_finding": finding_linked,
        "examined_but_cleared": examined_cleared,
        "uncovered": uncovered,
        "recommended_review_packets": packets,
        "likely_eval_miss_classes_recovered": likely,
        "detected": detected,
    }
    out = audit_path("output") / "getter_state_audit.json"
    out.write_text(json.dumps(report, indent=2))

    md = [f"# Getter-vs-state reconciliation audit\n",
          f"_Generated {ts} · manifest `{man_path}` · source_snippets={use_source} · NOT a gate_\n",
          f"Total getter/state-sensitive: **{len(detected)}** · high-risk **{len(high_risk)}** · "
          f"re-review **{len(re_review)}** · finding-linked **{len(finding_linked)}** · "
          f"cleared **{len(examined_cleared)}**\n",
          "## Previously cleared but high-risk getter/state reconciliation items\n"]
    if prev_cleared_hr:
        for x in sorted(prev_cleared_hr, key=lambda r: (r["category"], r["contract"] or "")):
            md.append(f"- **{x['contract']}.{x['name']}** ({x['category']}, {x['return_shape']}, "
                      f"consumer={x['consumer_hint']}) — `{x['file']}:{x['line']}` — "
                      f"cleared: _{(x['clear_reason'] or '')[:90]}_")
    else:
        md.append("- (none)")
    md.append("\n## Counts by category\n")
    for cat, n in by_category.most_common():
        md.append(f"- {cat}: {n}")
    md.append("\n## Recommended review packets\n")
    for p in packets:
        md.append(f"- **{p['packet_id']}** {p['label']} ({len(p['item_ids'])} items) — {p['files']}")
    md.append("\n## Likely residual miss classes recovered\n")
    for l in likely:
        md.append(f"- {l}")
    (audit_path("output") / "getter_state_audit.md").write_text("\n".join(md))
    print(f"[getter_state_audit] {len(detected)} sensitive · {len(high_risk)} high-risk · "
          f"{len(prev_cleared_hr)} previously-cleared-high-risk · wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
