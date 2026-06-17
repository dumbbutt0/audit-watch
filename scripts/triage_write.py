#!/usr/bin/env python3
"""
triage_write.py — Deterministic writer for the skill-in-session /triage flow.

Reads the /triage skill's decisions (data/triage/_decisions.json), validates them, and writes
the canonical triage buckets + per-finding markdown — identical artifacts to triage_findings.py,
but produced with no API call.

Decision record (one per finding) expected from the skill:
    {
      "finding_id": "OR-001",
      "triage_status": "submit|poc_required|downgraded|merged|rejected|unresolved_invariant",
      "recommended_severity": "High",
      "decision_reason": "...",
      "ice": {"impact": "...", "confidence": "...", "exploitability": "..."},
      "follow_up_packet": "...",
      "disproof": "..."            # REQUIRED if status is rejected/cleared on safety-net code
    }

Enforces the no-silent-clear rule: a reject/clear on safety-net code without a `disproof`
is re-routed to human_review_queue.jsonl rather than silently dropped.

Usage:
    python scripts/triage_write.py
    python scripts/triage_write.py --decisions data/triage/_decisions.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path
import reasoning_depth_utils as rdu

ROOT = Path(__file__).resolve().parent.parent
BUCKETS = {"submit", "poc_required", "downgraded", "merged", "rejected"}
VALID_STATUS = BUCKETS | {"unresolved_invariant"}
REQUIRED = ["finding_id", "triage_status", "recommended_severity", "decision_reason"]


def _rejection_depth_enforced() -> bool:
    """P245 #4 — default-off. Reads coverage_policy.rejection_depth_record_enforced from agent_policy."""
    try:
        pol = json.loads((ROOT / "config" / "agent_policy.json").read_text()).get("coverage_policy", {})
        return bool(pol.get("rejection_depth_record_enforced", False))
    except Exception:
        return False


def _load_bundle_index() -> dict[str, dict]:
    p = audit_path("data/triage", "_bundles", "index.json")
    if not p.exists():
        return {}
    return {r["finding_id"]: r for r in json.loads(p.read_text())}


def main() -> int:
    ap = argparse.ArgumentParser(description="Write triage buckets from /triage skill decisions")
    ap.add_argument("--decisions", default=None, help="Path to _decisions.json")
    args = ap.parse_args()

    dec_path = Path(args.decisions) if args.decisions else audit_path("data/triage", "_decisions.json")
    if not dec_path.exists():
        raise SystemExit(f"[error] decisions file not found: {dec_path}\n"
                         f"        Run triage_prepare.py, then the /triage skill, then this.")
    decisions = json.loads(dec_path.read_text())
    if isinstance(decisions, dict):
        decisions = decisions.get("decisions", [])

    index = _load_bundle_index()
    buckets: dict[str, list[dict]] = {b: [] for b in BUCKETS}
    human_queue: list[dict] = []
    errors: list[str] = []

    for d in decisions:
        fid = d.get("finding_id", "?")
        for f in REQUIRED:
            if not d.get(f):
                errors.append(f"{fid}: missing '{f}'")
        status = d.get("triage_status", "")
        if status not in VALID_STATUS:
            errors.append(f"{fid}: invalid triage_status '{status}'")
            continue

        is_safety_net = index.get(fid, {}).get("safety_net", False)

        # No-silent-clear enforcement: rejecting safety-net code requires a disproof.
        if status == "rejected" and is_safety_net and not d.get("disproof"):
            d = {**d, "triage_status": "unresolved_invariant",
                 "reroute_reason": "rejected safety-net code without attacker-path disproof"}
            status = "unresolved_invariant"

        # P245 #4 (default-off): a sensitive-area rejection requires a completed depth record. On an
        # incomplete record, REROUTE to human review (needs_depth) — preserve the candidate, explain the
        # missing fields. Never mints/relabels a finding (recall-protective only). The bundle index title
        # is merged in so area classification can see the finding's title, not just the decision text.
        if status == "rejected" and _rejection_depth_enforced():
            cls = rdu.classify_rejection({**index.get(fid, {}), **d})
            if cls["status"] == "needs_depth":
                d = {**d, "triage_status": "unresolved_invariant",
                     "reroute_reason": rdu.reroute_reason(cls),
                     "needs_depth": True,
                     "sensitive_areas": cls["areas"],
                     "missing_depth_fields": cls["missing"]}
                status = "unresolved_invariant"

        if status == "unresolved_invariant":
            human_queue.append(d)
            continue
        buckets[status].append(d)

        # per-finding markdown
        md = audit_path("data/triage", f"{fid}.md")
        ice = d.get("ice", {})
        md.write_text(
            f"# Triage — {fid}\n\n"
            f"**Status:** {status}  ·  **Severity:** {d.get('recommended_severity')}\n\n"
            f"**ICE:** I={ice.get('impact','?')} · C={ice.get('confidence','?')} · "
            f"E={ice.get('exploitability','?')}\n\n"
            f"## Decision reason\n{d.get('decision_reason','')}\n\n"
            f"## Follow-up packet\n{d.get('follow_up_packet','(none)')}\n"
            + (f"\n## Disproof\n{d['disproof']}\n" if d.get("disproof") else "")
        )

    if errors:
        print("Validation errors (nothing written):")
        for e in errors:
            print(f"  - {e}")
        return 1

    for b, rows in buckets.items():
        out = audit_path("data/triage", f"{b}.jsonl")
        out.write_text("".join(json.dumps(r) + "\n" for r in rows))
    if human_queue:
        hq = audit_path("data/triage", "human_review_queue.jsonl")
        with hq.open("a") as fh:
            for r in human_queue:
                fh.write(json.dumps(r) + "\n")

    print("[ok] Triage buckets written (skill-in-session path, no API):")
    for b, rows in buckets.items():
        print(f"     {b}: {len(rows)}")
    print(f"     unresolved_invariant → human_review_queue: {len(human_queue)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
