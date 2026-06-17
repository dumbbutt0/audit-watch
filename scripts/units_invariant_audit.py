#!/usr/bin/env python3
"""
units_invariant_audit.py — Decimals/units invariant detector + review-packet report.

Applies the units_invariant_patterns.json taxonomy (via units_invariant_taxonomy.classify) to the coverage
manifest. UNLIKE the cross-chain / token-standard lenses, the units signal lives in function BODIES, so this
detector READS THE SOURCE SNIPPET around each manifest source_span (file + start/end lines) and classifies on
it. Cross-references dispositions (finding / cleared / uncovered). Catches at read-time over the (frozen)
manifest — no rebuild — so eval3 integrity is preserved. Pure report; NOT a gate.

The headline "Previously cleared but high-risk units/decimals items" embodies the lesson: a function cleared
as "manipulation-resistant" (e.g. LibWell.getBeanTokenPriceFromTwaReserves) can still hide a units invariant
(the #184 hardcoded-1e18 reserve scaling).

Reads:  output/coverage_manifest.json (or --manifest), config/units_invariant_patterns.json,
        output/coverage_dispositions.json (optional), + source files for snippets.
Writes: output/units_invariant_audit.{json,md}

Usage: python scripts/units_invariant_audit.py [--manifest <path>] [--no-source]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
import units_invariant_taxonomy as units  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

CATEGORY_TO_MISS = {
    "assumed_18_decimals": ["#184 LibWell getBeanTokenPriceFromTwaReserves assumes 18 decimals"],
    "twa_reserves": ["#184 TWA-reserve 18-decimal assumption"],
    "reserve_units": ["#184 reserve-unit normalization"],
    "chainlink_decimals": ["#135/#267-adjacent oracle-decimal scaling"],
    "oracle_price_decimals": ["#135 oracle price-decimal scaling"],
    "shares_assets": ["ERC4626 shares/assets precision class"],
    "bdv_units": ["#184-adjacent BDV unit normalization"],
}

_FILE_CACHE: dict[str, list[str]] = {}


def _snippet(file_rel: str, start: int, end: int, use_source: bool) -> str:
    if not use_source or not file_rel or not start:
        return ""
    if file_rel not in _FILE_CACHE:
        p = ROOT / file_rel
        try:
            _FILE_CACHE[file_rel] = p.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            _FILE_CACHE[file_rel] = []
    lines = _FILE_CACHE[file_rel]
    if not lines:
        return ""
    a = max(0, (start or 1) - 1)
    b = min(len(lines), end or start or 1)
    return "\n".join(lines[a:b])[:4000]


def _load(path: Path, key: str):
    if not path.exists():
        return [] if key else {}
    try:
        d = json.loads(path.read_text())
        return d.get(key, []) if key else d
    except (OSError, json.JSONDecodeError):
        return [] if key else {}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", help="manifest path (default: live coverage_manifest.json)")
    ap.add_argument("--no-source", action="store_true", help="classify on signature only (no body snippet)")
    args = ap.parse_args()

    man_path = Path(args.manifest) if args.manifest else audit_path("output") / "coverage_manifest.json"
    items = _load(man_path, "items")
    if not items:
        raise SystemExit(f"[units_invariant_audit] no manifest items at {man_path}")
    tax = units.load_taxonomy()
    disp = {d["manifest_id"]: d for d in _load(audit_path("output") / "coverage_dispositions.json", "dispositions")}
    use_source = not args.no_source

    detected = []
    for it in items:
        if it.get("kind") not in ("function", "constructor", "initializer"):
            continue
        if not it.get("in_scope", True):
            continue
        span = it.get("source_span", {})
        snip = _snippet(it.get("file", ""), span.get("start_line"), span.get("end_line"), use_source)
        cls = units.classify(it.get("name", ""), it.get("signature", ""), it.get("file", ""),
                            it.get("contract", ""), snippet=snip, tags=it.get("tags"))
        if not cls.get("units_sensitive"):
            continue
        d = disp.get(it["id"], {})
        status = d.get("status")
        coverage = ("covered_by_finding" if status == "finding"
                    else "examined_but_cleared" if status == "cleared"
                    else "deferred" if status == "deferred_out_of_scope" else "uncovered")
        detected.append({
            "manifest_id": it["id"], "name": it.get("name"), "contract": it.get("contract"),
            "file": it.get("file"), "line": span.get("start_line"),
            "category": cls["category"], "risk_tags": cls["risk_tags"],
            "high_risk": units.is_high_risk(cls, tax), "severity_ceiling_hint": cls.get("severity_ceiling_hint"),
            "matched_on": cls.get("matched_on"), "coverage": coverage, "disposition_status": status,
            "finding_refs": d.get("finding_refs") or [],
            "clear_reason": (d.get("clear_reason") or "")[:160] if status == "cleared" else "",
        })

    by_cat = Counter(x["category"] for x in detected)
    high_risk = [x for x in detected if x["high_risk"]]
    cleared_high_risk = [x for x in detected if x["high_risk"] and x["coverage"] == "examined_but_cleared"]
    rereview = [x for x in detected if x["high_risk"] and x["coverage"] != "covered_by_finding"]

    packets = []
    groups = defaultdict(list)
    for x in rereview:
        groups[(x["category"], x["contract"] or "?")].append(x)
    for (cat, contract), xs in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        meta = tax.get("categories", {}).get(cat, {})
        packets.append({
            "packet_id": f"UNI-{cat}-{contract}", "label": "units_invariant", "category": cat,
            "contract": contract, "suggested_specialist": "arithmetic",
            "severity_ceiling_hint": meta.get("severity_ceiling_hint"),
            "item_ids": sorted(x["manifest_id"] for x in xs), "files": sorted({x["file"] for x in xs}),
            "review_prompt": (f"Re-review {len(xs)} {cat} item(s) in {contract} under the units lens "
                              f"(prompts/units_invariant_review.md). " + (meta.get("review_hint") or "")),
        })

    miss_classes = sorted({m for x in detected for m in CATEGORY_TO_MISS.get(x["category"], [])})

    ts = datetime.now(timezone.utc).isoformat()
    report = {
        "generated_at": ts, "manifest": str(man_path), "is_gate": False, "source_snippets": use_source,
        "total_units_sensitive": len(detected), "by_category": dict(by_cat.most_common()),
        "high_risk_count": len(high_risk),
        "previously_cleared_high_risk": cleared_high_risk,
        "covered_by_finding": [x["manifest_id"] for x in detected if x["coverage"] == "covered_by_finding"],
        "examined_but_cleared": [x["manifest_id"] for x in detected if x["coverage"] == "examined_but_cleared"],
        "uncovered": [x for x in detected if x["coverage"] == "uncovered"],
        "re_review_candidates": len(rereview), "recommended_review_packets": packets,
        "likely_eval_miss_classes_recovered": miss_classes, "detected": detected,
    }
    out = audit_path("output") / "units_invariant_audit.json"
    out.write_text(json.dumps(report, indent=2))

    md = [f"# Decimals / units invariant audit\n", f"_Generated {ts} · manifest `{man_path}` · source_snippets={use_source} · NOT a gate_\n",
          f"**{len(detected)}** units-sensitive · **{len(high_risk)}** high-risk · **{len(rereview)}** re-review candidates\n",
          "## ⚠ Previously cleared but high-risk units/decimals items",
          "_A function cleared as 'manipulation-resistant'/'standard' can still hide a units invariant "
          "(the #184 hardcoded-1e18 reserve scaling)._\n",
          "| name | contract | category | clear_reason |", "|---|---|---|---|"]
    for x in cleared_high_risk:
        md.append(f"| {x['name']} | {x['contract']} | {x['category']} | {x['clear_reason']} |")
    md += ["\n## By category", "| category | n |", "|---|---|"] + [f"| {c} | {n} |" for c, n in by_cat.most_common()]
    md += ["\n## Recommended review packets\n"]
    for p in packets:
        md.append(f"- **{p['packet_id']}** ({len(p['item_ids'])} items, sev≤{p['severity_ceiling_hint']}) → {p['suggested_specialist']}")
    md += ["\n## Likely eval miss classes this lens addresses\n"] + [f"- {m}" for m in miss_classes]
    (audit_path("output") / "units_invariant_audit.md").write_text("\n".join(md))

    print(f"[ok] units_invariant_audit → {out}")
    print(f"     detected {len(detected)} · high-risk {len(high_risk)} · re-review {len(rereview)} · source={use_source}")
    print(f"     by_category {dict(by_cat.most_common())}")
    print(f"     previously-cleared high-risk ({len(cleared_high_risk)}): {[(x['name'], x['category']) for x in cleared_high_risk][:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
