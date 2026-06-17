#!/usr/bin/env python3
"""
surface_mechanism_advisories.py — P135 routing/surfacing layer (NOT a detector).

Reads EXISTING mechanism-detector outputs and surfaces them as ADVISORY review_context so the issues the
mechanism layer already detects (P134) reach human review. It NEVER mints findings, NEVER assigns severity,
NEVER makes anything submission-ready, and NEVER changes detector/severity/submission logic.

Every surfaced entry is `advisory_only: true`, `submission_ready: false`, `requires_human_review: true`.
research_only / report_only detector status is preserved verbatim. Config-gated and capped; the master gate
`surface_mechanism_advisories: false` disables all surfacing.

Usage:
    python scripts/surface_mechanism_advisories.py [--manifest P] [--eval] [--quiet]
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
from audit_context import audit_path, get_audit_meta  # noqa: E402

ALLOWED_NEXT_STEPS = ["inspect_source", "run_deep_pass_value_provenance", "map_defenses",
                      "build_poc_if_confirmed", "reject_if_design_intended"]
FORBIDDEN_NEXT_STEPS = ["submit_directly", "assign_severity_without_impact",
                        "mark_confirmed_without_poc_or_human_review"]

# Per-detector adapter: where the list lives, field names, status, and the specialist to suggest.
DETECTOR_SPECS = {
    "connector_position_accounting": {
        "status": "advisory", "output": "connector_position_accounting_audit.json", "key": "detected",
        "contract": "contract", "function": "name", "file": "file", "mechanism": "shape",
        "confidence": "confidence", "line": None, "reason": "reason", "specialist": "logic"},
    "arithmetic_conservation": {
        "status": "advisory", "output": "arithmetic_conservation_audit.json", "key": "detected",
        "contract": "contract", "function": "name", "file": "file", "mechanism": "shape",
        "confidence": "confidence", "line": None, "reason": "reason", "specialist": "arithmetic"},
    "units_invariant": {
        "status": "report_only", "output": "units_invariant_audit.json", "key": "detected",
        "contract": "contract", "function": "name", "file": "file", "mechanism": "category",
        "confidence": None, "line": "line", "reason": None, "specialist": "arithmetic"},
    "semantic_tvl_completeness": {
        "status": "research_only", "output": "semantic_tvl_completeness_audit.json", "key": "candidates",
        "contract": "connector_contract", "function": "tvl_function", "file": "file",
        "mechanism": "finding_shape", "confidence": "confidence", "line": None, "reason": "reason",
        "specialist": "logic"},
    "registry_position_lifecycle": {
        "status": "research_only", "output": "registry_position_lifecycle_audit.json", "key": "candidates",
        "contract": "contract", "function": "function", "file": "file", "mechanism": "shape",
        "confidence": "confidence", "line": None, "reason": "reason", "specialist": "logic"},
}

DEFAULT_CFG = {
    "surface_mechanism_advisories": True,
    "surface_research_only_advisories": False,
    "mechanism_advisory_standalone_queue": False,
    "mechanism_advisory_max_per_detector": 10,
    "mechanism_advisory_max_total": 40,
    "mechanism_advisory_allowed_detectors": list(DETECTOR_SPECS.keys()),
}

DEEP_PASS_TAGS = {"oracle", "value", "accounting", "token"}
_LOOP_RE = re.compile(r"\b(for|while)\b\s*\(")
_CALL_RE = re.compile(r"\b[A-Za-z_]\w*\s*\(")


def load_cfg(eval_mode: bool = False) -> dict:
    cfg = dict(DEFAULT_CFG)
    try:
        pol = json.loads((Path(__file__).resolve().parent.parent / "config" / "agent_policy.json").read_text())
        cfg.update(pol.get("mechanism_advisory", {}))
    except (OSError, json.JSONDecodeError):
        pass
    if eval_mode:  # eval/research mode widens surfacing (still advisory-only)
        cfg["surface_research_only_advisories"] = True
        cfg["mechanism_advisory_standalone_queue"] = True
    return cfg


def _conf_for_units(raw: dict) -> str:
    return "high" if raw.get("high_risk") else "medium"


def normalize_hits(detector: str, raw_list: list, audit_id: str, source_path: str) -> list:
    """Pure: detector raw hits -> normalized advisory entries (no I/O)."""
    spec = DETECTOR_SPECS[detector]
    out = []
    for raw in raw_list:
        contract = raw.get(spec["contract"]) or ""
        function = raw.get(spec["function"]) or ""
        if not contract or not function:
            continue
        conf = _conf_for_units(raw) if detector == "units_invariant" else (raw.get(spec["confidence"]) or "medium")
        mech = raw.get(spec["mechanism"]) or "?"
        reason = raw.get(spec["reason"]) if spec["reason"] else None
        ev = reason or f"{detector} flagged {mech}" + (
            f" (tags={raw.get('risk_tags')})" if detector == "units_invariant" else "")
        out.append({
            "source_detector": detector,
            "detector_status": spec["status"],
            "advisory_only": True,
            "submission_ready": False,
            "requires_human_review": True,
            "audit_id": audit_id,
            "contract": contract,
            "function": function,
            "file_path": raw.get(spec["file"]) or "",
            "line": raw.get(spec["line"]) if spec["line"] else None,
            "mechanism_class": mech,
            "evidence_summary": str(ev)[:300],
            "confidence": str(conf).lower(),               # copied verbatim, never relabeled
            "route_reason": f"mechanism layer ({detector}/{spec['status']}) flagged this surface; the "
                            f"surface specialist may under-weight it — route to {spec['specialist']} review",
            "suggested_specialist": spec["specialist"],
            "related_candidate_id": None,
            "related_review_queue_id": None,
            "source_output_path": source_path,
            "allowed_next_steps": list(ALLOWED_NEXT_STEPS),
            "forbidden_next_steps": list(FORBIDDEN_NEXT_STEPS),
        })
    return out


def dedup(entries: list) -> list:
    seen, out = set(), []
    for e in entries:
        k = (e["file_path"], e["contract"], e["function"], e["mechanism_class"], e["source_detector"])
        if k in seen:
            continue
        seen.add(k)
        out.append(e)
    return out


def apply_status_gate(entries: list, cfg: dict) -> list:
    allowed = set(cfg["mechanism_advisory_allowed_detectors"])
    surf_research = cfg["surface_research_only_advisories"]
    kept = []
    for e in entries:
        if e["source_detector"] not in allowed:
            continue
        if e["detector_status"] == "research_only" and not surf_research:
            continue
        kept.append(e)
    return kept


_CONF_RANK = {"high": 3, "medium": 2, "low": 1}


def apply_caps(entries: list, cfg: dict) -> list:
    """Cap per-detector and total, KEEPING the highest-confidence entries first (stable) so caps never drop a
    high-signal hit in favor of a low one. General signal-priority — not target-specific."""
    per = int(cfg["mechanism_advisory_max_per_detector"])
    tot = int(cfg["mechanism_advisory_max_total"])
    ranked = sorted(entries, key=lambda e: _CONF_RANK.get(str(e.get("confidence", "")).lower(), 0), reverse=True)
    bydet: Counter = Counter()
    out = []
    for e in ranked:
        if bydet[e["source_detector"]] >= per or len(out) >= tot:
            continue
        bydet[e["source_detector"]] += 1
        out.append(e)
    return out


def attach_candidates(entries: list, merged: list) -> int:
    """Set related_candidate_id when a merged_findings candidate matches contract+function+file basename."""
    index = {}
    for f in merged:
        loc = f.get("location", {})
        fns = str(loc.get("function", "")).lower()
        base = Path(str(loc.get("file", ""))).name.lower()
        for fn in re.split(r"[\\/,;]| ", fns):
            if fn:
                index[(fn, base)] = f.get("id")
    n = 0
    for e in entries:
        key = (e["function"].lower(), Path(e["file_path"]).name.lower())
        if key in index:
            e["related_candidate_id"] = index[key]
            n += 1
    return n


def recommend_deep_pass(manifest_items: list, source_reader, cap: int) -> list:
    """review_context only: oracle/value/accounting-tagged fn with a loop + loop-carried call -> suggest the
    existing deep_pass_value_provenance prompt. NOT a finding, NO severity. General (no contract names)."""
    # Strongest value-provenance signal first (oracle > value > accounting > token) so the cap keeps the most
    # relevant loops. General tag-priority — not target-specific.
    _tagpri = {"oracle": 3, "value": 2, "accounting": 1, "token": 0}
    cands = sorted((it for it in manifest_items if it.get("kind") == "function"
                    and (DEEP_PASS_TAGS & set(it.get("tags", [])))),
                   key=lambda it: max((_tagpri.get(t, -1) for t in it.get("tags", [])), default=-1), reverse=True)
    recs, seen = [], set()
    for it in cands:
        sp = it.get("source_span", {})
        body = source_reader(it.get("file", ""), sp.get("start_line"), sp.get("end_line"))
        if not body or not _LOOP_RE.search(body):
            continue
        # a call inside the loop region (loop-carried conversion) — keep simple/general
        loop_region = body[_LOOP_RE.search(body).start():]
        if not _CALL_RE.search(loop_region):
            continue
        key = (it.get("contract"), it.get("name"))
        if key in seen:
            continue
        seen.add(key)
        recs.append({
            "source_detector": "deep_pass_router",
            "detector_status": "advisory",
            "advisory_only": True, "submission_ready": False, "requires_human_review": True,
            "review_context": True,
            "contract": it.get("contract"), "function": it.get("name"),
            "file_path": it.get("file"), "line": sp.get("start_line"),
            "mechanism_class": "value_provenance_loop",
            "recommended_prompt": "deep_pass_value_provenance",
            "prompt_reason": "multi-hop oracle/value loop / loop-carried quote/asset/value variable — "
                             "run deep_pass_value_provenance to trace identity-source vs quantity-source",
            "allowed_next_steps": list(ALLOWED_NEXT_STEPS),
            "forbidden_next_steps": list(FORBIDDEN_NEXT_STEPS),
        })
        if len(recs) >= cap:
            break
    return recs


def _read_body(file_rel: str, start, end) -> str:
    if not file_rel or not start:
        return ""
    p = Path(file_rel)
    if not p.is_absolute():
        p = Path(__file__).resolve().parent.parent / file_rel
    try:
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(lines[start - 1: (end or start)])
    except OSError:
        return ""


def build(cfg: dict, out_dir: Path, audit_id: str, manifest_items: list, merged: list,
          source_reader=_read_body) -> dict:
    if not cfg["surface_mechanism_advisories"]:
        return {"surfaced": False, "reason": "surface_mechanism_advisories=false", "advisories": [],
                "deep_pass_recommendations": []}
    raw_entries = []
    for det, spec in DETECTOR_SPECS.items():
        path = out_dir / spec["output"]
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        raw_entries += normalize_hits(det, data.get(spec["key"], []), audit_id, str(path))
    entries = apply_caps(apply_status_gate(dedup(raw_entries), cfg), cfg)
    attached = attach_candidates(entries, merged)
    recs = recommend_deep_pass(manifest_items, source_reader,
                               int(cfg["mechanism_advisory_max_per_detector"]))
    return {
        "schema_version": "mechanism_advisory_1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "surfaced": True,
        "routing_allowed": False, "research_only_summary": True, "submission_ready": False,
        "config": cfg,
        "summary": {
            "total_advisories": len(entries),
            "attached_to_candidate": attached,
            "by_detector": dict(Counter(e["source_detector"] for e in entries)),
            "by_status": dict(Counter(e["detector_status"] for e in entries)),
            "deep_pass_recommendations": len(recs),
        },
        "advisories": entries,
        "deep_pass_recommendations": recs,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Surface mechanism-detector output as advisory review_context.")
    ap.add_argument("--manifest")
    ap.add_argument("--eval", action="store_true", help="eval/research mode (surface research-only + standalone queue)")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    cfg = load_cfg(eval_mode=args.eval)
    out_dir = audit_path("output")
    audit_id = get_audit_meta().get("audit_id", "unknown")
    man_path = Path(args.manifest) if args.manifest else out_dir / "coverage_manifest.json"
    manifest_items = []
    if man_path.exists():
        try:
            manifest_items = json.loads(man_path.read_text()).get("items", [])
        except (OSError, json.JSONDecodeError):
            pass
    merged_path = out_dir / "merged_findings.json"
    merged = []
    if merged_path.exists():
        try:
            merged = json.loads(merged_path.read_text()).get("findings", [])
        except (OSError, json.JSONDecodeError):
            pass

    report = build(cfg, out_dir, audit_id, manifest_items, merged)
    out = out_dir / "mechanism_advisory_context.json"
    out.write_text(json.dumps(report, indent=2))

    # Optional, gated: append advisory-only review_context entries to the human review queue.
    queued = 0
    if report.get("surfaced") and cfg["mechanism_advisory_standalone_queue"]:
        qpath = audit_path("data") / "triage" / "human_review_queue.jsonl"
        qpath.parent.mkdir(parents=True, exist_ok=True)
        with qpath.open("a") as fh:
            for i, e in enumerate(report["advisories"]):
                qe = {
                    "advisory_id": f"ADV-{e['source_detector'][:4].upper()}-{i:03d}",
                    "review_context": True, "advisory_only": True, "submission_ready": False,
                    "requires_human_review": True, "finding_id": None, "recommended_severity": None,
                    "source_detector": e["source_detector"], "detector_status": e["detector_status"],
                    "contract": e["contract"], "function": e["function"], "file": e["file_path"],
                    "mechanism_class": e["mechanism_class"], "evidence_summary": e["evidence_summary"],
                    "related_candidate_id": e["related_candidate_id"],
                    "queued_at": datetime.now(timezone.utc).isoformat(),
                }
                fh.write(json.dumps(qe) + "\n")
                queued += 1
        report["summary"]["standalone_queue_entries"] = queued
        out.write_text(json.dumps(report, indent=2))

    if not args.quiet:
        if not report.get("surfaced"):
            print(f"[surface_mechanism_advisories] DISABLED ({report.get('reason')}) — 0 surfaced")
        else:
            s = report["summary"]
            print(f"[surface_mechanism_advisories] advisory_only · {s['total_advisories']} advisories "
                  f"(by_detector {s['by_detector']}, by_status {s['by_status']}), "
                  f"attached {s['attached_to_candidate']}, deep_pass_recs {s['deep_pass_recommendations']}, "
                  f"queued {queued} · wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
