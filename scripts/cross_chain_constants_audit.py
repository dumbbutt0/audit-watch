#!/usr/bin/env python3
"""
cross_chain_constants_audit.py — Cross-chain-sensitive constant detector + review-packet report.

Applies the cross_chain_constants.json taxonomy (via cross_chain_taxonomy.classify) to the coverage
manifest and cross-references each match against the coverage dispositions to separate:
  * covered_by_finding      (disposition status == 'finding')
  * examined_but_cleared    (status == 'cleared')  <-- the BRIDGE / block-time RE-REVIEW class
  * deferred                (status == 'deferred_out_of_scope')
  * uncovered               (no disposition)

Because the constants already exist in the (frozen) manifest, this catches them at READ TIME — it does
NOT require a manifest rebuild, so it never touches eval3 artifacts. Pure report; NOT a gate.

Reads:  output/coverage_manifest.json (or --manifest), config/cross_chain_constants.json,
        output/coverage_dispositions.json (optional, for coverage cross-ref).
Writes: output/cross_chain_constants_audit.{json,md}

Usage:
    python scripts/cross_chain_constants_audit.py [--manifest <path>]
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
import cross_chain_taxonomy as xchain  # noqa: E402

# category -> answer-key miss subs the lens would help convert (eval-impact estimate)
CATEGORY_TO_MISS = {
    "bridge": ["#142 BRIDGE address mismatch prevents migration"],
    "messenger": ["#142 (cross-domain message routing)"],
    "oracle_aggregator": ["#135 LibUsdOracle broken on L2", "#133 (oracle-on-L2 class)"],
    "sequencer_feed": ["#267 ETH/USD heartbeat / L2 sequencer staleness"],
    "heartbeat": ["#267 ETH/USD 1hr heartbeat wrong for L2"],
    "block_time": ["#469 Hardcoded block-time assumptions in LibDibbler"],
    "merkle_root": ["#320 Hardcoded MERKLE_ROOT makes contract unusable"],
    "chain_id": ["#228 domain-separator / chainId family"],
    "l1_token": ["#133/#135 token-address-on-L2"],
    "l2_token": ["#133 token-address-on-L2 (CREATE2 mismatch)"],
    "implementation": ["#320-adjacent reseed deploy placeholder"],
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
        raise SystemExit(f"[cross_chain_constants_audit] no manifest items at {man_path}")
    tax = xchain.load_taxonomy()
    disp = {d["manifest_id"]: d for d in _load(audit_path("output") / "coverage_dispositions.json", "dispositions")}

    detected = []
    for it in items:
        if it.get("kind") not in ("constant", "immutable", "address", "magic_number"):
            continue
        # use inline tag if the manifest already carries it; else classify at read-time
        if it.get("cross_chain_sensitive"):
            cls = {"cross_chain_sensitive": True, "category": it.get("cross_chain_category"),
                   "risk_tags": [k for k in ("chain_specific", "hardcoded_address", "hardcoded_chain_assumption",
                                             "oracle_dependency", "bridge_dependency", "timing_dependency")
                                 if it.get(k)],
                   "severity_ceiling_hint": it.get("cross_chain_severity_hint")}
        else:
            cls = xchain.classify(it.get("name", ""), it.get("signature", ""), it.get("file", ""))
        if not cls.get("cross_chain_sensitive"):
            continue
        d = disp.get(it["id"], {})
        status = d.get("status")
        coverage = ("covered_by_finding" if status == "finding"
                    else "examined_but_cleared" if status == "cleared"
                    else "deferred" if status == "deferred_out_of_scope"
                    else "uncovered")
        detected.append({
            "manifest_id": it["id"], "name": it.get("name"), "kind": it.get("kind"),
            "contract": it.get("contract"), "file": it.get("file"),
            "line": it.get("source_span", {}).get("start_line"),
            "category": cls["category"], "risk_tags": cls["risk_tags"],
            "high_risk": xchain.is_high_risk(cls, tax),
            "severity_ceiling_hint": cls.get("severity_ceiling_hint"),
            "in_scope": it.get("in_scope", True),
            "coverage": coverage, "disposition_status": status,
            "finding_refs": d.get("finding_refs") or [],
            "clear_reason": (d.get("clear_reason") or "")[:160] if status == "cleared" else "",
            "signature": (it.get("signature") or "")[:160],
        })

    by_cat = Counter(x["category"] for x in detected)
    by_cov = Counter(x["coverage"] for x in detected)
    high_risk = [x for x in detected if x["high_risk"]]
    # re-review candidates: high-risk AND not already a finding (cleared/uncovered/deferred)
    rereview = [x for x in detected if x["high_risk"] and x["coverage"] != "covered_by_finding"]

    # recommended review packets (deep_pass_queue packet shape) grouped by (category, contract)
    packets = []
    groups = defaultdict(list)
    for x in rereview:
        groups[(x["category"], x["contract"] or "?")].append(x)
    for (cat, contract), xs in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        meta = tax.get("categories", {}).get(cat, {})
        files = sorted({x["file"] for x in xs})
        packets.append({
            "packet_id": f"XCC-{cat}-{contract}",
            "label": "cross_chain_constants", "category": cat, "contract": contract,
            "suggested_specialist": "cross_chain",
            "severity_ceiling_hint": meta.get("severity_ceiling_hint"),
            "item_ids": sorted(x["manifest_id"] for x in xs),
            "files": files,
            "review_prompt": (f"Re-review {len(xs)} {cat} constant(s) in {contract} under the cross-chain "
                              f"lens (prompts/cross_chain_constants_review.md). " + (meta.get("review_hint") or "")),
        })

    miss_classes = sorted({m for x in detected for m in CATEGORY_TO_MISS.get(x["category"], [])})

    ts = datetime.now(timezone.utc).isoformat()
    report = {
        "generated_at": ts, "manifest": str(man_path), "is_gate": False,
        "total_cross_chain_sensitive": len(detected),
        "by_category": dict(by_cat.most_common()),
        "by_coverage": dict(by_cov),
        "high_risk_count": len(high_risk),
        "re_review_candidates": len(rereview),
        "covered_by_finding": [x["manifest_id"] for x in detected if x["coverage"] == "covered_by_finding"],
        "examined_but_cleared": [x for x in detected if x["coverage"] == "examined_but_cleared"],
        "uncovered": [x for x in detected if x["coverage"] == "uncovered"],
        "recommended_review_packets": packets,
        "likely_eval_miss_classes_recovered": miss_classes,
        "detected": detected,
    }
    out = audit_path("output") / "cross_chain_constants_audit.json"
    out.write_text(json.dumps(report, indent=2))

    md = [f"# Cross-chain-sensitive constants audit\n", f"_Generated {ts} · manifest `{man_path}` · NOT a gate_\n",
          f"**{len(detected)}** cross-chain-sensitive constants · **{len(high_risk)}** high-risk · "
          f"**{len(rereview)}** re-review candidates (high-risk, not yet a finding)\n",
          "## By category", "| category | n |", "|---|---|"]
    for c, n in by_cat.most_common():
        md.append(f"| {c} | {n} |")
    md += ["\n## By coverage disposition", "| coverage | n |", "|---|---|"]
    for c, n in by_cov.items():
        md.append(f"| {c} | {n} |")
    md += ["\n## Examined-but-cleared (RE-REVIEW class — the #142/#469 lesson)\n",
           "| name | category | contract | clear_reason |", "|---|---|---|---|"]
    for x in report["examined_but_cleared"]:
        md.append(f"| {x['name']} | {x['category']} | {x['contract']} | {x['clear_reason']} |")
    md += ["\n## Recommended review packets\n"]
    for p in packets:
        md.append(f"- **{p['packet_id']}** ({len(p['item_ids'])} items, sev≤{p['severity_ceiling_hint']}) → {p['suggested_specialist']}")
    md += ["\n## Likely eval miss classes this lens addresses\n"] + [f"- {m}" for m in miss_classes]
    (audit_path("output") / "cross_chain_constants_audit.md").write_text("\n".join(md))

    print(f"[ok] cross_chain_constants_audit → {out}")
    print(f"     detected {len(detected)} · high-risk {len(high_risk)} · re-review {len(rereview)} · "
          f"categories {dict(by_cat.most_common())}")
    print(f"     coverage {dict(by_cov)}")
    bridge = [x for x in detected if x["category"] in ("bridge", "messenger")]
    print(f"     BRIDGE/messenger detected: {[(x['name'], x['coverage']) for x in bridge]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
