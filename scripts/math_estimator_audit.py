#!/usr/bin/env python3
"""
math_estimator_audit.py — 9th recall lens: flag math-ESTIMATOR / guard / formula surfaces that must be
proven by independent re-derivation rather than NatSpec/code agreement. Mirrors units_invariant_audit.py.

Reads output/coverage_manifest.json, classifies each in-scope function/constructor via
math_estimator_taxonomy.classify_manifest_item(), and writes output/math_estimator_audit.{json,md}. Pure
report (no gate); validate_math_estimator_clears.py is the enforcement point. Suggests the
`math_estimator_review` specialist for high-risk surfaces.
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
import math_estimator_taxonomy as me  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def _load(path: Path, key: str) -> list:
    try:
        return json.loads(path.read_text()).get(key, [])
    except (OSError, json.JSONDecodeError):
        return []


def main() -> int:
    man_path = audit_path("output") / "coverage_manifest.json"
    items = _load(man_path, "items")
    tax = me.load_taxonomy()
    disp = {d["manifest_id"]: d for d in _load(audit_path("output") / "coverage_dispositions.json", "dispositions")}

    detected, high_risk, cleared_high_risk = [], [], []
    by_domain: Counter = Counter()
    packets_by = defaultdict(list)

    for it in items:
        if it.get("kind") not in ("function", "constructor", "initializer"):
            continue
        if not it.get("in_scope", True):
            continue
        cls = me.classify_manifest_item(it, taxonomy=tax)
        if not cls["math_estimator_sensitive"]:
            continue
        mid = it["id"]
        d = disp.get(mid, {})
        status = d.get("status", "unassigned")
        hr = me.is_high_risk(cls, tax)
        entry = {
            "manifest_id": mid, "contract": it.get("contract"), "name": it.get("name"),
            "file": it.get("file"), "math_domain": cls["math_domain"], "risk_tags": cls["risk_tags"],
            "matched_on": cls["matched_on"], "high_risk": hr, "attack_surface_score": it.get("attack_surface_score", 0),
            "coverage_status": status,
            "has_math_proof": bool(d.get("math_estimator_proof")),
            "finding_refs": d.get("finding_refs", []),
            "review_hint": cls["review_hint"], "severity_ceiling_hint": cls["severity_ceiling_hint"],
        }
        detected.append(entry)
        by_domain[cls["math_domain"]] += 1
        if hr:
            high_risk.append(mid)
            # a high-risk math item already cleared WITHOUT a math proof is the H-11 risk surface
            if status == "cleared" and not d.get("math_estimator_proof") and not d.get("finding_refs"):
                cleared_high_risk.append(mid)
            packets_by[cls["math_domain"]].append(mid)

    packets = [{"math_domain": dom, "item_ids": ids, "suggested_specialist": "math_estimator_review",
                "review_prompt": (f"Independently re-derive the {dom} formula/invariant for these "
                                  f"{len(ids)} item(s) vs the whitepaper/model; do NOT clear on NatSpec/code "
                                  f"agreement. Produce a math_estimator_proof (intended vs implemented "
                                  f"formula, scaling, signedness, edge cases, evidence).")}
               for dom, ids in sorted(packets_by.items(), key=lambda kv: -len(kv[1]))]

    ts = datetime.now(timezone.utc).isoformat()
    report = {
        "lens": "math_estimator", "generated_at": ts, "manifest": str(man_path), "is_gate": False,
        "total_math_estimator_sensitive": len(detected), "by_domain": dict(by_domain.most_common()),
        "high_risk_count": len(high_risk),
        "cleared_high_risk_without_proof": cleared_high_risk,
        "recommended_review_packets": packets,
        "detected": detected,
    }
    (audit_path("output") / "math_estimator_audit.json").write_text(json.dumps(report, indent=2))

    md = ["# Math-estimator lens", "",
          f"- math-estimator-sensitive items: **{len(detected)}**",
          f"- high-risk: **{len(high_risk)}**",
          f"- high-risk cleared WITHOUT a math proof (H-11 risk surface): **{len(cleared_high_risk)}**",
          f"- by domain: {dict(by_domain.most_common())}", "",
          "| domain | contract.name | high_risk | status | proof | file |",
          "|---|---|---|---|---|---|"]
    for e in sorted(detected, key=lambda e: (not e["high_risk"], e["math_domain"])):
        md.append(f"| {e['math_domain']} | {e['contract']}.{e['name']} | {e['high_risk']} | "
                  f"{e['coverage_status']} | {'yes' if e['has_math_proof'] else 'no'} | {e['file'].split('/')[-1]} |")
    (audit_path("output") / "math_estimator_audit.md").write_text("\n".join(md) + "\n")

    print(f"[math-estimator] detected {len(detected)} · high-risk {len(high_risk)} · "
          f"cleared-high-risk-without-proof {len(cleared_high_risk)} · by_domain {dict(by_domain)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
