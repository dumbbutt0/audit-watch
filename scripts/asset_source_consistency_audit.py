#!/usr/bin/env python3
"""
asset_source_consistency_audit.py — recall lens: flags functions where the amount's ORIGIN asset-source
family may differ from the family funds are TRANSFERRED/accounted from (collateral vs supply vs native vs
token). NOT a gate; never mutates dispositions; never finding-mints. Two-signal, FP-tight. Recovers Recall
H-05 (leave transfers genesisBalance — a supply amount — out of collateralSource). Writes
output/asset_source_consistency_audit.{json,md}.

Usage: python scripts/asset_source_consistency_audit.py [--manifest <path>] [--no-source]
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
import asset_source_consistency_taxonomy as asc  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
_FILE_CACHE: dict[str, list[str]] = {}


def _snippet(file_rel, start, end, use_source):
    if not use_source or not file_rel or not start:
        return ""
    if file_rel not in _FILE_CACHE:
        try:
            _FILE_CACHE[file_rel] = (ROOT / file_rel).read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            _FILE_CACHE[file_rel] = []
    lines = _FILE_CACHE[file_rel]
    return "\n".join(lines[max(0, (start or 1) - 1):min(len(lines), end or start or 1)])[:4000] if lines else ""


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
    ap.add_argument("--manifest")
    ap.add_argument("--no-source", action="store_true")
    args = ap.parse_args()

    man_path = Path(args.manifest) if args.manifest else audit_path("output") / "coverage_manifest.json"
    items = _load(man_path, "items")
    if not items:
        raise SystemExit(f"[asset_source_consistency_audit] no manifest items at {man_path}")
    tax = asc.load_taxonomy()
    disp = {d["manifest_id"]: d for d in _load(audit_path("output") / "coverage_dispositions.json", "dispositions")}
    use_source = not args.no_source

    def _cov(mid):
        st = disp.get(mid, {}).get("status")
        return ("covered_by_finding" if st == "finding" else "examined_but_cleared" if st == "cleared"
                else "deferred" if st == "deferred_out_of_scope" else "uncovered")

    detected = []
    for it in items:
        if it.get("kind") not in ("function", "constructor", "initializer"):
            continue
        if not it.get("in_scope", True):
            continue
        span = it.get("source_span", {})
        snip = _snippet(it.get("file", ""), span.get("start_line"), span.get("end_line"), use_source)
        cls = asc.classify(it.get("name", ""), it.get("signature", ""), it.get("file", ""),
                           it.get("contract", ""), snippet=snip, tags=it.get("tags"))
        if not cls.get("asset_source_sensitive"):
            continue
        high = asc.is_high_risk(cls, tax)
        detected.append({
            "manifest_id": it["id"], "name": it.get("name"), "contract": it.get("contract"),
            "file": it.get("file"), "line": span.get("start_line"),
            "category": cls["category"], "high_risk": high,
            # required output fields
            "amount_origin": " | ".join(cls["families"]),
            "asset_source": " | ".join(cls["transfer_families"]) or " | ".join(cls["transfer_sources"]) or "(accounting-only)",
            "accounting_state_updated": cls["has_accounting"],
            "actual_transfer_source": " | ".join(cls["transfer_sources"]) or "(none-local)",
            "mismatch": (f"function mixes asset-source families {cls['families']} and moves/accounts via "
                         f"{cls['transfer_families'] or cls['transfer_sources'] or 'accounting'} — the amount's "
                         f"origin family may differ from the transfer source"),
            "attacker_controlled_parameter": "amount / value argument",
            "impact_ceiling": cls["severity_ceiling_hint"],
            "coverage": _cov(it["id"]),
        })

    high_risk = [x for x in detected if x["high_risk"]]
    high_risk_ids = sorted({x["manifest_id"] for x in high_risk})
    by_cat = Counter(x["category"] for x in detected)
    packets = [{"packet_id": f"ASC-{x['contract']}-{x['name']}", "label": "asset_source_consistency",
                "suggested_specialist": "asset_source_review", "manifest_id": x["manifest_id"],
                "amount_origin": x["amount_origin"], "asset_source": x["asset_source"],
                "review_prompt": (f"{x['contract']}.{x['name']} mixes asset-source families "
                                  f"({x['amount_origin']}) and transfers from ({x['asset_source']}). Confirm the "
                                  f"amount's origin family EQUALS the transfer source family (e.g. a supply/"
                                  f"genesis amount must be paid from supplySource, not collateralSource).")}
               for x in high_risk if x["coverage"] != "covered_by_finding"]

    ts = datetime.now(timezone.utc).isoformat()
    report = {
        "lens": "asset_source_consistency", "generated_at": ts, "manifest": str(man_path), "is_gate": False,
        "source_snippets": use_source, "total_sensitive": len(detected), "by_category": dict(by_cat.most_common()),
        "high_risk_count": len(high_risk), "high_risk_manifest_ids": high_risk_ids,
        "recommended_review_packets": packets, "detected": detected,
    }
    out = audit_path("output") / "asset_source_consistency_audit.json"
    out.write_text(json.dumps(report, indent=2))

    md = [f"# Asset-source vs amount-origin consistency audit\n",
          f"_Generated {ts} · manifest `{man_path}` · NOT a gate · high-risk → needs_deep_pass_\n",
          f"**{len(detected)}** source-mixing functions · **{len(high_risk)}** high-risk\n",
          "## High-risk (>=2 asset-source families + fund movement)\n",
          "| contract.name | amount_origin | transfer_source | coverage |", "|---|---|---|---|"]
    for x in high_risk:
        md.append(f"| {x['contract']}.{x['name']} | {x['amount_origin']} | {x['asset_source']} | {x['coverage']} |")
    (audit_path("output") / "asset_source_consistency_audit.md").write_text("\n".join(md) + "\n")

    print(f"[ok] asset_source_consistency_audit → {out}")
    print(f"     sensitive {len(detected)} · high-risk {len(high_risk)} · by_category {dict(by_cat.most_common())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
