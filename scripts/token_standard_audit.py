#!/usr/bin/env python3
"""
token_standard_audit.py — Token-standard interaction detector + review-packet report.

Applies the token_standard_patterns.json taxonomy (via token_standard_taxonomy.classify) to the coverage
manifest and cross-references each match against the coverage dispositions to separate covered_by_finding /
examined_but_cleared / deferred / uncovered. Mirrors cross_chain_constants_audit.py.

Catches the token-standard surfaces at READ TIME over the (frozen) manifest — no rebuild — so eval3
integrity is preserved. Pure report; NOT a gate.

The headline "Previously cleared but high-risk token-standard items" section embodies the BRIDGE lesson:
ERC1155 acceptance-check / safe-mint / safe-transfer functions that were cleared as "verbatim OZ / standard
reimp" are exactly the #272/#273 surfaces and must be re-reviewed under a token-standard-semantic lens.

Reads:  output/coverage_manifest.json (or --manifest), config/token_standard_patterns.json,
        output/coverage_dispositions.json (optional).
Writes: output/token_standard_audit.{json,md}

Usage: python scripts/token_standard_audit.py [--manifest <path>]
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
import token_standard_taxonomy as tstd  # noqa: E402

CATEGORY_TO_MISS = {
    "erc1155_acceptance_check": ["#273 High Risk DoS in ERC1155 Token Minting"],
    "erc1155_receiver_callback": ["#273 ERC1155 mint/transfer receiver DoS"],
    "erc1155_mint": ["#273 ERC1155 mint DoS / stuck tokens"],
    "erc1155_batch_mint": ["#273 ERC1155 batch-mint DoS"],
    "erc1155_transfer": ["#272 Fertilizer ERC1155 NFT loss in migration"],
    "erc1155_batch_transfer": ["#272 Fertilizer ERC1155 NFT loss in migration"],
    "erc1155_supply_accounting": ["#272 Fertilizer NFT / supply mis-accounting"],
    "cross_standard_confusion": ["#272 (token-standard-confused transfer)"],
}


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
    args = ap.parse_args()

    man_path = Path(args.manifest) if args.manifest else audit_path("output") / "coverage_manifest.json"
    items = _load(man_path, "items")
    if not items:
        raise SystemExit(f"[token_standard_audit] no manifest items at {man_path}")
    tax = tstd.load_taxonomy()
    disp = {d["manifest_id"]: d for d in _load(audit_path("output") / "coverage_dispositions.json", "dispositions")}

    detected = []
    for it in items:
        if it.get("kind") not in ("function", "constructor", "initializer"):
            continue
        if not it.get("in_scope", True):
            continue  # production review surface only (mocks/interfaces are out of scope)
        cls = tstd.classify(it.get("name", ""), it.get("signature", ""), it.get("file", ""),
                            it.get("contract", ""))
        if not cls.get("token_standard_sensitive"):
            continue
        d = disp.get(it["id"], {})
        status = d.get("status")
        coverage = ("covered_by_finding" if status == "finding"
                    else "examined_but_cleared" if status == "cleared"
                    else "deferred" if status == "deferred_out_of_scope"
                    else "uncovered")
        detected.append({
            "manifest_id": it["id"], "name": it.get("name"), "contract": it.get("contract"),
            "file": it.get("file"), "line": it.get("source_span", {}).get("start_line"),
            "standard": cls["standard"], "category": cls["category"], "risk_tags": cls["risk_tags"],
            "high_risk": tstd.is_high_risk(cls, tax), "severity_ceiling_hint": cls.get("severity_ceiling_hint"),
            "in_scope": it.get("in_scope", True), "coverage": coverage, "disposition_status": status,
            "finding_refs": d.get("finding_refs") or [],
            "clear_reason": (d.get("clear_reason") or "")[:160] if status == "cleared" else "",
            "matched_on": cls.get("matched_on"), "signature": (it.get("signature") or "")[:160],
        })

    by_std = Counter(x["standard"] for x in detected)
    by_cat = Counter(x["category"] for x in detected)
    high_risk = [x for x in detected if x["high_risk"]]
    erc1155 = [x for x in detected if x["standard"] == "ERC1155"]
    cleared_high_risk = [x for x in detected if x["high_risk"] and x["coverage"] == "examined_but_cleared"]
    rereview = [x for x in detected if x["high_risk"] and x["coverage"] != "covered_by_finding"]

    packets = []
    groups = defaultdict(list)
    for x in rereview:
        groups[(x["category"], x["contract"] or "?")].append(x)
    for (cat, contract), xs in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        meta = tax.get("categories", {}).get(cat, {})
        packets.append({
            "packet_id": f"TST-{cat}-{contract}", "label": "token_standard", "category": cat,
            "contract": contract, "suggested_specialist": "token_integration",
            "severity_ceiling_hint": meta.get("severity_ceiling_hint"),
            "item_ids": sorted(x["manifest_id"] for x in xs),
            "files": sorted({x["file"] for x in xs}),
            "review_prompt": (f"Re-review {len(xs)} {cat} item(s) in {contract} under the token-standard lens "
                              f"(prompts/token_standard_review.md). " + (meta.get("review_hint") or "")),
        })

    miss_classes = sorted({m for x in detected for m in CATEGORY_TO_MISS.get(x["category"], [])})

    ts = datetime.now(timezone.utc).isoformat()
    report = {
        "generated_at": ts, "manifest": str(man_path), "is_gate": False,
        "total_token_standard_sensitive": len(detected),
        "by_standard": dict(by_std.most_common()), "by_category": dict(by_cat.most_common()),
        "high_risk_count": len(high_risk), "erc1155_count": len(erc1155),
        "previously_cleared_high_risk": cleared_high_risk,
        "covered_by_finding": [x["manifest_id"] for x in detected if x["coverage"] == "covered_by_finding"],
        "examined_but_cleared": [x["manifest_id"] for x in detected if x["coverage"] == "examined_but_cleared"],
        "uncovered": [x for x in detected if x["coverage"] == "uncovered"],
        "re_review_candidates": len(rereview),
        "recommended_review_packets": packets,
        "likely_eval_miss_classes_recovered": miss_classes,
        "detected": detected,
    }
    out = audit_path("output") / "token_standard_audit.json"
    out.write_text(json.dumps(report, indent=2))

    md = [f"# Token-standard interaction audit\n", f"_Generated {ts} · manifest `{man_path}` · NOT a gate_\n",
          f"**{len(detected)}** token-standard-sensitive · **{len(erc1155)}** ERC1155 · **{len(high_risk)}** high-risk "
          f"· **{len(rereview)}** re-review candidates\n",
          "## ⚠ Previously cleared but high-risk token-standard items",
          "_The BRIDGE/#273 lesson: a token fn cleared as 'verbatim OZ / standard reimp' may still hide a "
          "receiver-DoS / stuck-token / supply-accounting bug._\n",
          "| name | contract | category | clear_reason |", "|---|---|---|---|"]
    for x in cleared_high_risk:
        md.append(f"| {x['name']} | {x['contract']} | {x['category']} | {x['clear_reason']} |")
    md += ["\n## By standard", "| standard | n |", "|---|---|"] + [f"| {s} | {n} |" for s, n in by_std.most_common()]
    md += ["\n## By category", "| category | n |", "|---|---|"] + [f"| {c} | {n} |" for c, n in by_cat.most_common()]
    md += ["\n## Recommended review packets\n"]
    for p in packets:
        md.append(f"- **{p['packet_id']}** ({len(p['item_ids'])} items, sev≤{p['severity_ceiling_hint']}) → {p['suggested_specialist']}")
    md += ["\n## Likely eval miss classes this lens addresses\n"] + [f"- {m}" for m in miss_classes]
    (audit_path("output") / "token_standard_audit.md").write_text("\n".join(md))

    print(f"[ok] token_standard_audit → {out}")
    print(f"     detected {len(detected)} · ERC1155 {len(erc1155)} · high-risk {len(high_risk)} · re-review {len(rereview)}")
    print(f"     by_standard {dict(by_std)} · by_category {dict(by_cat.most_common())}")
    print(f"     previously-cleared high-risk ({len(cleared_high_risk)}): {[(x['name'], x['category']) for x in cleared_high_risk]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
