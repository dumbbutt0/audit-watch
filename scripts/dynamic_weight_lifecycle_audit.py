#!/usr/bin/env python3
"""
dynamic_weight_lifecycle_audit.py — recall lens (F1): flag dynamic-weight / Balancer-V3 weight-lifecycle
surfaces (setWeights/update/onSwap/computeBalance) whose weight-set lifecycle invariants (normalized-sum,
per-weight bounds, epsilon guard-rail, updateInterval, interpolation-horizon/staleness) may be incomplete on a
permissionless update path. Mirrors math_estimator_audit.py.

Reads output/coverage_manifest.json, classifies each in-scope function via
dynamic_weight_lifecycle_taxonomy.classify_manifest_item(), and writes
output/dynamic_weight_lifecycle_audit.{json,md}. PURE RE-SURFACE LENS (no gate, no severity, no finding):
validate_dynamic_weight_lifecycle_clears.py + the coverage_sweep_write enforcement route a thin clear of these
surfaces to needs_deep_pass (dynamic_weight_lifecycle_review). Family-gated (the names self-scope to
dynamic-weight pools — 0 hits on non-dynamic-weight corpora).
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
import dynamic_weight_lifecycle_taxonomy as dwl  # noqa: E402


def _load(path: Path, key: str) -> list:
    try:
        return json.loads(path.read_text()).get(key, [])
    except (OSError, json.JSONDecodeError):
        return []


def main() -> int:
    man_path = audit_path("output") / "coverage_manifest.json"
    items = _load(man_path, "items")
    tax = dwl.load_taxonomy()
    disp = {d["manifest_id"]: d for d in _load(audit_path("output") / "coverage_dispositions.json", "dispositions")}

    detected, high_risk, cleared_high_risk = [], [], []
    for it in items:
        if it.get("kind") not in ("function", "constructor", "initializer"):
            continue
        if not it.get("in_scope", True):
            continue
        cls = dwl.classify_manifest_item(it, taxonomy=tax)
        if not cls["lifecycle_sensitive"]:
            continue
        mid = it["id"]
        d = disp.get(mid, {})
        status = d.get("status", "unassigned")
        hr = dwl.is_high_risk(cls)
        detected.append({
            "manifest_id": mid, "contract": it.get("contract"), "name": it.get("name"), "file": it.get("file"),
            "lifecycle_domain": cls["lifecycle_domain"], "missing_lifecycle_checks": cls["missing_lifecycle_checks"],
            "present_lifecycle_checks": cls["present_lifecycle_checks"], "high_risk": hr,
            "attack_surface_score": it.get("attack_surface_score", 0), "coverage_status": status,
            "has_lifecycle_proof": bool(d.get("dynamic_weight_lifecycle_proof")),
            "finding_refs": d.get("finding_refs", []),
        })
        if hr:
            high_risk.append(mid)
            if status == "cleared" and not d.get("dynamic_weight_lifecycle_proof") and not d.get("finding_refs"):
                cleared_high_risk.append(mid)

    ts = datetime.now(timezone.utc).isoformat()
    report = {
        "lens": "dynamic_weight_lifecycle", "generated_at": ts, "manifest": str(man_path),
        "is_gate": False, "routes_in_production": False, "re_surface_only": True,
        "total_lifecycle_sensitive": len(detected), "high_risk_count": len(high_risk),
        "cleared_high_risk_without_proof": cleared_high_risk,
        "review_specialist": "dynamic_weight_lifecycle_review",
        "review_prompt": ("Deep-trace the weight-set lifecycle for these surfaces: verify normalized-sum, "
                          "per-weight bounds, epsilon guard-rail, updateInterval, and interpolation/staleness "
                          "are each enforced on every PERMISSIONLESS update path. Produce a "
                          "dynamic_weight_lifecycle_proof; do NOT clear on a thin local explanation."),
        "detected": detected,
    }
    (audit_path("output") / "dynamic_weight_lifecycle_audit.json").write_text(json.dumps(report, indent=2))

    md = ["# Dynamic-weight lifecycle lens (F1)", "",
          f"- lifecycle-sensitive items: **{len(detected)}**",
          f"- high-risk (missing ≥1 lifecycle check): **{len(high_risk)}**",
          f"- high-risk cleared WITHOUT a lifecycle proof: **{len(cleared_high_risk)}**", "",
          "| contract.name | missing checks | high_risk | status | proof | file |",
          "|---|---|---|---|---|---|"]
    for e in sorted(detected, key=lambda e: (not e["high_risk"], e["contract"] or "")):
        md.append(f"| {e['contract']}.{e['name']} | {','.join(e['missing_lifecycle_checks'])} | {e['high_risk']} | "
                  f"{e['coverage_status']} | {'yes' if e['has_lifecycle_proof'] else 'no'} | {(e['file'] or '').split('/')[-1]} |")
    (audit_path("output") / "dynamic_weight_lifecycle_audit.md").write_text("\n".join(md) + "\n")

    print(f"[dynamic-weight-lifecycle] detected {len(detected)} · high-risk {len(high_risk)} · "
          f"cleared-high-risk-without-proof {len(cleared_high_risk)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
