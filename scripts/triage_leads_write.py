#!/usr/bin/env python3
"""
triage_leads_write.py — Validate + bucket finding-lead / PoC-queue triage verdicts (deterministic, no LLM).

Ingests triage specialist verdict files (data/triage_leads/_verdict_*.json, each
{"group_id","verdicts":[{id, verdict, ...}]}) and buckets each verdict into output/triage/ after
validating the required-field set per verdict type. Incomplete verdicts are REJECTED (kept pending,
logged) — never force-accepted, never overclaimed. Does NOT touch merged_findings.json / dispositions
/ the /triage skill's data/triage (this is the separate finding-lead triage layer).

Verdict types + required fields:
  confirmed_finding   : id, manifest_refs, attacker_entrypoint, external_reachability, violated_invariant,
                        impact, severity_ceiling, evidence_spans, duplicate_check, min_poc_or_existing_proof
  false_positive      : id, evidence_spans, guard_or_invariant, why_hypothesis_fails
  duplicate_or_known  : id, duplicate_of, overlap_explanation, new_entrypoint_or_same_root
  needs_unit_poc /
  needs_fork_poc      : id, attacker_entrypoint, preconditions, state_before, state_after,
                        impact_hypothesis, severity_ceiling, min_poc_plan, duplicate_check
  out_of_scope /
  insufficient_evidence : id, reason

Usage:
    python scripts/triage_leads_write.py --verdicts <file_or_glob>   (repeatable; default: all data/triage_leads/_verdict_*.json)
"""
from __future__ import annotations

import argparse
import glob
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402

REQUIRED = {
    "confirmed_finding": ["manifest_refs", "attacker_entrypoint", "external_reachability",
                          "violated_invariant", "impact", "severity_ceiling", "evidence_spans",
                          "duplicate_check", "min_poc_or_existing_proof"],
    "false_positive": ["evidence_spans", "guard_or_invariant", "why_hypothesis_fails"],
    "duplicate_or_known": ["duplicate_of", "overlap_explanation", "new_entrypoint_or_same_root"],
    "needs_unit_poc": ["attacker_entrypoint", "preconditions", "state_before", "state_after",
                       "impact_hypothesis", "severity_ceiling", "min_poc_plan", "duplicate_check"],
    "needs_fork_poc": ["attacker_entrypoint", "preconditions", "state_before", "state_after",
                       "impact_hypothesis", "severity_ceiling", "min_poc_plan", "duplicate_check"],
    "out_of_scope": ["reason"],
    "insufficient_evidence": ["reason"],
}
BUCKET = {
    "confirmed_finding": "confirmed_findings.json",
    "false_positive": "false_positives.json",
    "duplicate_or_known": "duplicates.json",
    "needs_unit_poc": "poc_required.json",
    "needs_fork_poc": "poc_required.json",
}


def _nonempty(v) -> bool:
    if isinstance(v, str):
        return bool(v.strip())
    return bool(v)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verdicts", action="append", default=[])
    args = ap.parse_args()

    files = []
    for pat in (args.verdicts or [str(audit_path("data/triage_leads") / "_verdict_*.json")]):
        files.extend(sorted(glob.glob(pat)))
    if not files:
        raise SystemExit("[triage_leads_write] no verdict files found.")

    out_dir = audit_path("output") / "triage"
    out_dir.mkdir(parents=True, exist_ok=True)
    buckets: dict[str, list] = {b: [] for b in set(BUCKET.values())}
    results, rejected, oos = [], [], []
    seen = set()

    for f in files:
        try:
            payload = json.loads(Path(f).read_text())
        except json.JSONDecodeError as e:
            rejected.append({"file": f, "_reject": f"invalid JSON: {e}"}); continue
        gid = payload.get("group_id", Path(f).stem)
        for v in payload.get("verdicts", []):
            vid = v.get("id") or v.get("lead_id") or v.get("manifest_id")
            vt = v.get("verdict")
            if not vid or vt not in REQUIRED:
                rejected.append({"group": gid, "id": vid, "_reject": f"missing id or invalid verdict '{vt}'"}); continue
            if vid in seen:
                rejected.append({"group": gid, "id": vid, "_reject": "duplicate verdict id"}); continue
            missing = [k for k in REQUIRED[vt] if not _nonempty(v.get(k))]
            if missing:
                rejected.append({"group": gid, "id": vid, "verdict": vt, "_reject": f"missing {missing}"}); continue
            seen.add(vid)
            rec = {**v, "group_id": gid, "triaged_at": datetime.now(timezone.utc).isoformat()}
            results.append({"id": vid, "verdict": vt, "group_id": gid,
                            "severity_ceiling": v.get("severity_ceiling"),
                            "summary": (v.get("reasoning_summary") or v.get("impact") or v.get("reason") or "")[:200]})
            if vt in ("out_of_scope", "insufficient_evidence"):
                oos.append(rec)
            else:
                buckets[BUCKET[vt]].append(rec)

    for fn, rows in buckets.items():
        p = out_dir / fn
        existing = json.loads(p.read_text()).get("items", []) if p.exists() else []
        p.write_text(json.dumps({"items": existing + rows, "updated_at": datetime.now(timezone.utc).isoformat()}, indent=2))
    (out_dir / "high_priority_triage_results.json").write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "verdicts_in": len(results) + len(rejected) + len(oos),
        "accepted": len(results), "rejected": len(rejected),
        "out_of_scope_or_insufficient": oos, "results": results}, indent=2))
    if rejected:
        rp = out_dir / "rejected_triage.json"
        prev = json.loads(rp.read_text()).get("rejected", []) if rp.exists() else []
        rp.write_text(json.dumps({"rejected": prev + rejected}, indent=2))

    # append triage_status onto finding_leads.json (no delete)
    fl_path = audit_path("output") / "deep_pass_execution" / "finding_leads.json"
    if fl_path.exists():
        fl = json.loads(fl_path.read_text())
        status_by_id = {r["id"]: r["verdict"] for r in results}
        for l in fl.get("leads", []):
            if l.get("lead_id") in status_by_id:
                l["triage_status"] = status_by_id[l["lead_id"]]
        fl_path.write_text(json.dumps(fl, indent=2))

    from collections import Counter
    by_v = Counter(r["verdict"] for r in results)
    print(f"[ok] triage_leads_write: accepted {len(results)}, rejected {len(rejected)}, oos {len(oos)}")
    print(f"     by verdict: {dict(by_v)}")
    for fn, rows in buckets.items():
        if rows:
            print(f"     {fn}: +{len(rows)}")
    for r in rejected[:8]:
        print(f"     REJECT {r.get('id')}: {r['_reject']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
