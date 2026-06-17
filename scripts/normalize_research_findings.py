#!/usr/bin/env python3
"""
normalize_research_findings.py — READ-ONLY Research Finding Normalization Layer.

Maps the candidates of one or more research-detector `*_audit.json` outputs (e.g. multicall_invariant_audit.json,
permit_asset_binding_audit.json) into ONE comparable normalized record shape (schemas/research_finding_normalized.
schema.json), so confidence / declared-severity-potential / signal-quality / review-priority can be compared across
detector families. Adding a future detector = add one entry to config/research_finding_normalization.json.

STRICTLY RESEARCH-ONLY:
  * Every normalized record carries routing_allowed:false and research_only:true.
  * Normalization NEVER changes a detector's confidence — it copies it verbatim and only RANKS (review_priority).
  * Defensive guard: a source whose report says routes_in_production:true OR routed_manifest_ids != [] is REFUSED
    (the layer never launders a routed source).
  * It does NOT route, does NOT auto-assign per-finding severity, and does NOT call the production
    exploitability / submission / gate engine. It only reads detector outputs and writes one normalized file.

Usage:
  python scripts/normalize_research_findings.py --audit <a.json> [--audit <b.json> ...] \
      --out research_findings_normalized.json [--quiet]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "config" / "research_finding_normalization.json"
SCHEMA_VERSION = "1.0"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def _registry() -> dict:
    return _load_json(REGISTRY)


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def review_priority(confidence: str, declared_sev: str, suppressed: bool, reg: dict) -> tuple[float, dict]:
    """Transparent, deterministic ranking. NEVER alters confidence — only ranks. Factors echoed into why_priority."""
    cw = reg["confidence_weights"].get(confidence, 0.2)
    sw = reg["severity_weights"].get(declared_sev, 0.2)
    pen = reg["suppression_penalty"] if suppressed else 0.0
    score = _clamp01(cw * sw - pen)
    return score, {"confidence_weight": cw, "severity_weight": sw, "suppression_penalty": pen}


def normalize_source(audit_path: Path, reg: dict) -> tuple[dict, list[dict]]:
    """Return (source_record, [normalized records]) for one *_audit.json. Refuses routed sources."""
    rep = _load_json(audit_path)
    detector = rep.get("lens", "unknown")
    rel = str(audit_path.resolve())
    try:
        rel = str(audit_path.resolve().relative_to(ROOT))
    except ValueError:
        pass

    # defensive guard: never normalize a source that is (or claims to be) production-routed
    routed = bool(rep.get("routes_in_production")) or bool(rep.get("routed_manifest_ids"))
    spec = reg["detectors"].get(detector)
    dv = (spec or reg["unknown_detector_fallback"])["detector_version"]
    if routed:
        return ({"detector": detector, "detector_version": dv, "source_audit_path": rel,
                 "accepted": False, "reason": "source is production-routed (routes_in_production/routed_manifest_ids) "
                                               "— refused; the normalization layer is research-only"}, [])

    spec = spec or reg["unknown_detector_fallback"]
    signal_type = spec["signal_type"]
    declared_sev = spec["declared_severity_potential"]
    evidence_fields = spec["evidence_fields"]

    records = []
    for c in rep.get("candidates", []):
        contract = c.get("contract", "")
        function = c.get("function", c.get("multicall_function", ""))
        surface = f"{contract}.{function}".strip(".")
        confidence = c.get("confidence", "needs_context")          # copied VERBATIM — never changed
        suppressed = (c.get("suppression_status") not in (None, "", "none"))
        rp, why = review_priority(confidence, declared_sev, suppressed, reg)
        evidence = {k: c[k] for k in evidence_fields if k in c and c[k] not in (None, "", [], {})}
        lens_id = c.get("lens_id") or f"{surface}:{c.get('finding_shape','')}"
        candidate_id = f"{detector}:{lens_id}:{hashlib.sha256((rel + lens_id).encode()).hexdigest()[:8]}"
        records.append({
            "detector": detector, "detector_version": dv, "schema_version": SCHEMA_VERSION,
            "candidate_id": candidate_id, "source_audit_path": rel,
            "signal_type": signal_type, "finding_shape": c.get("finding_shape", ""),
            "confidence": confidence, "candidate_surface": surface,
            "file_line_refs": c.get("file_line_refs", ""),
            "evidence": evidence, "declared_severity_potential": declared_sev,
            "review_priority": round(rp, 4), "why_priority": why,
            "suppression_status": c.get("suppression_status", "none"),
            "routing_allowed": False, "research_only": True,
        })
    return ({"detector": detector, "detector_version": dv, "source_audit_path": rel,
             "accepted": True, "reason": f"{len(records)} candidate(s) normalized"}, records)


def main() -> int:
    ap = argparse.ArgumentParser(description="Read-only research finding normalization layer.")
    ap.add_argument("--audit", action="append", default=[], help="a detector *_audit.json (repeatable)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    if not args.audit:
        raise SystemExit("[normalize_research_findings] need at least one --audit <path>")

    reg = _registry()
    sources, records = [], []
    for a in args.audit:
        p = Path(a)
        if not p.is_absolute() and not p.exists():
            p = ROOT / a
        if not p.exists():
            sources.append({"detector": "unknown", "source_audit_path": a, "accepted": False,
                            "reason": "file not found"})
            continue
        src, recs = normalize_source(p, reg)
        sources.append(src)
        records.extend(recs)

    records.sort(key=lambda r: r["review_priority"], reverse=True)
    out = {
        "schema_version": SCHEMA_VERSION, "generated_at": datetime.now(timezone.utc).isoformat(),
        "routing_allowed": False,
        "sources": sources, "records": records,
        "summary": {
            "total_records": len(records),
            "by_detector": dict(Counter(r["detector"] for r in records)),
            "by_confidence": dict(Counter(r["confidence"] for r in records)),
            "top_by_review_priority": [f"{r['candidate_surface']} ({r['detector']},{r['confidence']},"
                                       f"rp={r['review_priority']})" for r in records[:10]],
        },
    }
    Path(args.out).write_text(json.dumps(out, indent=2))
    if not args.quiet:
        acc = sum(1 for s in sources if s["accepted"])
        print(f"[normalize_research_findings] RESEARCH-ONLY · sources {acc}/{len(sources)} accepted · "
              f"records {len(records)} · by_detector {out['summary']['by_detector']} · wrote {args.out}")
        for s in sources:
            if not s["accepted"]:
                print(f"   ! refused {s['detector']} ({s['source_audit_path']}): {s['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
