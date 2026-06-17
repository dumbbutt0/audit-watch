#!/usr/bin/env python3
"""
min_confirm_gate.py — Minimal confirmation gate before submission-readiness (deterministic, no LLM).

The Beanstalk eval shipped 8 FPs out of 48 (speculative reachability, unproven preconditions). This
gate requires every submission-ready candidate (triage status submit / poc_required) to carry the
basic confirmation skeleton — attacker entrypoint, affected manifest_refs, preconditions, expected
impact, relevant guards + why they don't stop it, a smallest-PoC/repro plan, a severity ceiling, a
confidence score, and a not-a-duplicate reason. Missing dimensions => block (so vague candidates can't
reach submit). It maps onto EXISTING fields (ite / ice_chain / proof_of_concept / triage
follow_up_packet / confidence / duplicate_of) — it does not require new authoring for well-formed findings.

Not over-aggressive: only the submit + poc_required buckets are gated; early candidates elsewhere are
untouched. Override: AUDITWATCH_MINCONFIRM_OVERRIDE=1.

Usage:
    python scripts/min_confirm_gate.py [--quiet]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
GATED_BUCKETS = ("submit", "poc_required")


def _policy() -> dict:
    try:
        return json.loads((ROOT / "config" / "agent_policy.json").read_text()).get("coverage_policy", {})
    except Exception:
        return {}


def _jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for ln in path.read_text().splitlines():
        ln = ln.strip()
        if ln:
            try:
                out.append(json.loads(ln))
            except json.JSONDecodeError:
                pass
    return out


def _merged_index() -> dict[str, dict]:
    p = audit_path("output") / "merged_findings.json"
    if not p.exists():
        return {}
    try:
        return {f.get("id") or f.get("finding_id"): f
                for f in json.loads(p.read_text()).get("findings", [])}
    except (json.JSONDecodeError, OSError):
        return {}


def _nonempty(*vals) -> bool:
    for v in vals:
        if isinstance(v, str) and v.strip():
            return True
        if isinstance(v, (list, dict)) and v:
            return True
    return False


def check_finding(f: dict, t: dict, require_manifest_refs: bool) -> list[str]:
    """Return list of missing confirmation dimensions for one candidate."""
    ite = f.get("ite", {}) or {}
    ice = f.get("ice_chain", {}) or {}
    # ice_chain is commonly a human-readable string (e.g. "I=High · C=High · E=Permissionless");
    # the structured-field lookups below require a dict, so coerce non-dicts to {} defensively.
    if not isinstance(ice, dict):
        ice = {}
    tice = t.get("ice", {}) or {}
    if not isinstance(tice, dict):
        tice = {}
    fup = t.get("follow_up_packet", "") or ""
    loc = f.get("location", {}) or {}
    missing = []

    if not _nonempty(ite.get("intent"), loc.get("function"), tice.get("exploitability"), fup):
        missing.append("attacker_entrypoint")
    if require_manifest_refs and not _nonempty(f.get("manifest_refs")):
        missing.append("manifest_refs")
    if not _nonempty(ice.get("exploit_path"), f.get("critical_assumptions"), fup, tice.get("exploitability")):
        missing.append("preconditions")
    if not _nonempty(f.get("impact"), ice.get("impact"), tice.get("impact")):
        missing.append("expected_impact")
    if not _nonempty(ite.get("evasion"), f.get("defense_mapping"), fup):
        missing.append("relevant_guards/why_they_fail")
    if not _nonempty(f.get("proof_of_concept"), ice.get("exploit_path"), fup):
        missing.append("smallest_poc_or_plan")
    if not _nonempty(ice.get("severity_ceiling"), f.get("severity"), t.get("recommended_severity")):
        missing.append("severity_ceiling")
    if not _nonempty(f.get("confidence"), tice.get("confidence")):
        missing.append("confidence")
    # not-a-duplicate: either it's not flagged duplicate, or it carries a reason
    if f.get("duplicate_of") and not _nonempty(t.get("decision_reason"), f.get("cross_agent_note")):
        missing.append("not_duplicate_reason")
    return missing


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    pol = _policy()
    require_refs = pol.get("finding_requires_manifest_refs", True)
    override = os.environ.get("AUDITWATCH_MINCONFIRM_OVERRIDE", "").strip() in ("1", "true", "yes", "on")

    merged = _merged_index()
    triage_dir = audit_path("data/triage")
    candidates: dict[str, dict] = {}
    for bucket in GATED_BUCKETS:
        for row in _jsonl(triage_dir / f"{bucket}.jsonl"):
            fid = row.get("finding_id")
            if fid:
                candidates[fid] = row

    results = []
    blocking = []
    for fid, trow in sorted(candidates.items()):
        f = merged.get(fid, {})
        missing = check_finding(f, trow, require_refs)
        confirmed = not missing
        results.append({"finding_id": fid, "confirmed": confirmed, "missing": missing,
                        "severity": trow.get("recommended_severity", f.get("severity", "?"))})
        if not confirmed:
            (blocking if not override else []).append(fid)

    passed = len(blocking) == 0
    report = {
        "passed": passed, "generated_at": datetime.now(timezone.utc).isoformat(),
        "override_active": override, "require_manifest_refs": require_refs,
        "candidates": len(candidates), "confirmed": sum(1 for r in results if r["confirmed"]),
        "blocking": blocking, "results": results,
    }
    (audit_path("output") / "min_confirm_gate.json").write_text(json.dumps(report, indent=2))

    if not args.quiet:
        print(f"Min-confirm gate: {'PASS' if passed else 'BLOCK'}" + (" (OVERRIDE)" if override else ""))
        print(f"  candidates {len(candidates)} · confirmed {report['confirmed']} · blocking {len(blocking)}")
        for r in results:
            if not r["confirmed"]:
                print(f"    {r['finding_id']} ({r['severity']}): missing {', '.join(r['missing'])}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
