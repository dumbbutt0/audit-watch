#!/usr/bin/env python3
"""
recipient_custody_audit.py — recall lens for bridge/escrow ASSET DELIVERY compatibility: safe-vs-raw
transfer, non-receiver lock (safe delivery to a recipient with no onERC721Received/onERC1155Received
capability check), no retry/recovery path for stuck assets, and custody-released-but-trapped. Recovers
ArkProject AK-M2 (NFTs locked when bridged to a contract without onERC721Received). NOT a gate; never
mutates dispositions. Writes output/recipient_custody_audit.{json,md}.

Usage: python scripts/recipient_custody_audit.py [--manifest <path>] [--no-source]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
import recipient_custody_taxonomy as rc  # noqa: E402

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
        raise SystemExit(f"[recipient_custody_audit] no manifest items at {man_path}")
    tax = rc.load_taxonomy()
    disp = {d["manifest_id"]: d for d in _load(audit_path("output") / "coverage_dispositions.json", "dispositions")}
    use_source = not args.no_source

    # contract-level recovery presence: does any in-scope function name look like a retry/recover path?
    recovery_re = "|".join(tax.get("recovery_signals", []))
    contracts_with_recovery = set()
    for it in items:
        if recovery_re and re.search(recovery_re, (it.get("name") or ""), re.IGNORECASE):
            contracts_with_recovery.add(it.get("contract"))

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
        cls = rc.classify(it.get("name", ""), it.get("signature", ""), it.get("file", ""),
                          it.get("contract", ""), snippet=snip, tags=it.get("tags"))
        if not cls.get("recipient_custody_sensitive"):
            continue
        high = rc.is_high_risk(cls, tax)
        no_recovery = it.get("contract") not in contracts_with_recovery
        category = cls["category"]
        if high and no_recovery and category == "non_receiver_lock":
            category = "non_receiver_lock"  # primary; recovery gap noted in flag
        detected.append({
            "manifest_id": it["id"], "name": it.get("name"), "contract": it.get("contract"),
            "file": it.get("file"), "line": span.get("start_line"),
            "category": category, "high_risk": high, "no_retry_recovery": no_recovery,
            "severity_ceiling_hint": cls["severity_ceiling_hint"], "matched_on": cls["matched_on"],
            "coverage": _cov(it["id"]),
        })

    by_cat = Counter(x["category"] for x in detected)
    high_risk = [x for x in detected if x["high_risk"]]
    review = [x for x in high_risk if x["coverage"] != "covered_by_finding"]
    packets = [{"packet_id": f"RCP-{x['contract']}-{x['name']}", "label": "recipient_custody",
                "suggested_specialist": "bridge_custody_review", "manifest_id": x["manifest_id"],
                "category": x["category"], "severity_ceiling_hint": x["severity_ceiling_hint"],
                "no_retry_recovery": x["no_retry_recovery"],
                "review_prompt": (f"{x['contract']}.{x['name']} delivers an asset ({x['category']}); verify the "
                                  f"recipient can receive it (onERC721Received/onERC1155Received) and that a failed "
                                  f"delivery has a retry/recovery path (no_retry_recovery={x['no_retry_recovery']}).")}
               for x in review]

    ts = datetime.now(timezone.utc).isoformat()
    report = {
        "lens": "recipient_custody", "generated_at": ts, "manifest": str(man_path), "is_gate": False,
        "source_snippets": use_source, "total_recipient_custody_sensitive": len(detected),
        "by_category": dict(by_cat.most_common()), "high_risk_count": len(high_risk),
        "routed_to_bridge_custody_review": [x["manifest_id"] for x in review],
        "recommended_review_packets": packets, "detected": detected,
    }
    out = audit_path("output") / "recipient_custody_audit.json"
    out.write_text(json.dumps(report, indent=2))

    md = [f"# Recipient / custody compatibility audit\n", f"_Generated {ts} · manifest `{man_path}` · NOT a gate_\n",
          f"**{len(detected)}** delivery-sensitive · **{len(high_risk)}** high-risk · **{len(review)}** → bridge/custody review\n",
          "## By category", "| category | n |", "|---|---|"] + [f"| {c} | {n} |" for c, n in by_cat.most_common()]
    md += ["\n## High-risk (safe delivery without a receiver-capability check / custody-trapped)\n",
           "| contract.name | category | no_retry_recovery | coverage |", "|---|---|---|---|"]
    for x in high_risk:
        md.append(f"| {x['contract']}.{x['name']} | {x['category']} | {x['no_retry_recovery']} | {x['coverage']} |")
    (audit_path("output") / "recipient_custody_audit.md").write_text("\n".join(md) + "\n")

    print(f"[ok] recipient_custody_audit → {out}")
    print(f"     detected {len(detected)} · high-risk {len(high_risk)} · routed-to-review {len(review)}")
    print(f"     by_category {dict(by_cat.most_common())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
