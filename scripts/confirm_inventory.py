#!/usr/bin/env python3
"""
confirm_inventory.py — Build the reachability-confirmation worklist (deterministic, no LLM, no judgement).

Reads the candidate finding sets (merged_findings + eval_findings) + manifest + dispositions + the eval
duplicate map (if present) and emits a normalized per-candidate record for the reachability analyzer. This
script does NOT judge truth — it just assembles the worklist. READ-ONLY on all inputs; writes only
output/confirm/confirm_inventory.json (never mutates eval3 artifacts).

Usage: python scripts/confirm_inventory.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402

# the confirmation skeleton fields we expect a well-formed candidate to carry (presence only, not truth)
CONFIRM_FIELDS = ["attacker_entrypoint", "manifest_refs", "preconditions", "impact", "guards",
                  "poc_or_repro", "severity", "confidence"]


def _load(path: Path, key: str):
    if not path.exists():
        return [] if key else {}
    try:
        d = json.loads(path.read_text())
        return d.get(key, []) if key else d
    except (OSError, json.JSONDecodeError):
        return [] if key else {}


def _present(f: dict) -> tuple[list, list]:
    ite = f.get("ite") or {}
    ice = f.get("ice_chain") or {}
    # ice_chain is commonly a human-readable string; structured lookups below need a dict.
    if not isinstance(ice, dict):
        ice = {}
    if not isinstance(ite, dict):
        ite = {}
    have = {
        "attacker_entrypoint": bool(ice.get("consumer_function") or ite.get("technique") or f.get("attacker_entrypoint")),
        "manifest_refs": bool(f.get("manifest_refs")),
        "preconditions": bool(ite.get("technique") or ice.get("exploit_path") or f.get("preconditions")),
        "impact": bool(ice.get("impact") or f.get("impact")),
        "guards": bool(ite.get("evasion") or f.get("guards") or f.get("why_guards_fail")),
        "poc_or_repro": bool(f.get("proof_of_concept") or f.get("min_poc_plan") or f.get("min_poc_or_existing_proof")),
        "severity": bool(f.get("severity") or f.get("severity_ceiling")),
        "confidence": bool(f.get("confidence")),
    }
    return [k for k in CONFIRM_FIELDS if have.get(k)], [k for k in CONFIRM_FIELDS if not have.get(k)]


def main() -> int:
    out_dir = audit_path("output") / "confirm"
    out_dir.mkdir(parents=True, exist_ok=True)

    merged = _load(audit_path("output") / "merged_findings.json", "findings")
    evalf = _load(audit_path("output") / "eval_ready" / "eval_findings.json", "eval_findings")
    dupmap = _load(audit_path("output") / "eval_ready" / "eval_duplicate_map.json", None)
    dup_by_cluster = {}
    for c in (dupmap.get("clusters") or []) if isinstance(dupmap, dict) else []:
        dup_by_cluster[c.get("root_cause_id")] = c.get("duplicate_of")

    candidates = []

    for f in merged:
        loc = f.get("location") or {}
        ice = f.get("ice_chain") or {}
        ite = f.get("ite") or {}
        if not isinstance(ice, dict):
            ice = {}
        if not isinstance(ite, dict):
            ite = {}
        present, missing = _present(f)
        fns = [loc.get("function")] if loc.get("function") else []
        candidates.append({
            "finding_id": f.get("id"), "title": f.get("title", ""), "severity": f.get("severity", ""),
            "layer": "merged", "classification": None,
            "affected_contracts": [f.get("_contract")] if f.get("_contract") else [],
            "affected_functions": [x for x in fns if x],
            "manifest_refs": f.get("manifest_refs") or [],
            "claimed_entrypoint": ice.get("consumer_function") or ite.get("intent") or "",
            "claimed_sink": loc.get("function") or "", "claimed_sink_file": loc.get("file") or "",
            "claimed_impact": ice.get("impact") or f.get("impact") or "",
            "existing_confidence": f.get("confidence", ""),
            "consumer_found": ice.get("consumer_found"),
            "source_evidence": {"file": loc.get("file"), "line_start": loc.get("line_start"),
                                "technique": ite.get("technique")},
            # NOTE: cross_agent_refs = corroboration ("also found by agent X"), NOT a duplicate-of another
            # finding — do not treat it as a duplicate relationship. Only an explicit duplicate_of counts.
            "duplicate_relationships": [f.get("duplicate_of")] if f.get("duplicate_of") else [],
            "corroborating_agents": [r for r in (f.get("cross_agent_refs") or []) if r],
            "required_confirmation_fields": {"present": present, "missing": missing},
        })

    for e in evalf:
        present = [k for k in CONFIRM_FIELDS if e.get({"attacker_entrypoint": "title"}.get(k, k)) or
                   (k == "manifest_refs" and e.get("manifest_refs")) or
                   (k == "impact" and e.get("impact_hypothesis")) or (k == "severity" and e.get("severity_ceiling")) or
                   (k == "confidence" and e.get("confidence"))]
        missing = [k for k in CONFIRM_FIELDS if k not in present]
        candidates.append({
            "finding_id": e.get("eval_id"), "title": e.get("title", ""),
            "severity": e.get("severity_ceiling", ""), "layer": "eval",
            "classification": e.get("classification"),
            "affected_contracts": e.get("affected_contracts") or [],
            "affected_functions": e.get("affected_functions") or [],
            "manifest_refs": e.get("manifest_refs") or [],
            "claimed_entrypoint": (e.get("affected_functions") or [""])[0],
            "claimed_sink": (e.get("affected_functions") or [""])[0], "claimed_sink_file": "",
            "claimed_impact": e.get("impact_hypothesis") or e.get("title") or "",
            "existing_confidence": e.get("confidence", ""), "consumer_found": None,
            "source_evidence": {"evidence_spans": e.get("evidence_spans")},
            "duplicate_relationships": [e.get("duplicate_of")] if e.get("duplicate_of") else [],
            "required_confirmation_fields": {"present": present, "missing": missing},
        })

    ts = datetime.now(timezone.utc).isoformat()
    payload = {"generated_at": ts, "count": len(candidates),
               "merged_count": len(merged), "eval_count": len(evalf),
               "note": "worklist only — no truth judgement (see confirm_reachability.py)",
               "candidates": candidates}
    (out_dir / "confirm_inventory.json").write_text(json.dumps(payload, indent=2))
    print(f"[ok] confirm_inventory → {out_dir / 'confirm_inventory.json'}")
    print(f"     candidates: {len(candidates)} ({len(merged)} merged + {len(evalf)} eval)")
    incomplete = sum(1 for c in candidates if c["required_confirmation_fields"]["missing"])
    print(f"     with missing confirmation fields: {incomplete}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
