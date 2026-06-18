#!/usr/bin/env python3
"""
precision_gate.py — Real-world submission PRECISION gate (deterministic, no LLM).

The first batch of adjudicated bounty outcomes (documentation/real_world_results.json) rejected 8/8 valid
PoCs on three axes that have NOTHING to do with bug validity: live-deployment reachability, novelty/duplicate,
and design-acceptance. submission_risk_audit.py already SCORES those axes (output/submission_risk.json) but is
advisory-only. This gate turns the *confident negatives* on those axes into a submission-blocking decision —
modeled exactly on confirm_gate.py (two modes, override env, never wired into eval/full).

  --mode eval        (default) classify + advise; exit 0 (NEVER blocks the eval candidate set).
  --mode submission  HARD-FAIL (exit 1) on a READY High/Critical finding with a CONFIDENT NEGATIVE:
                       - deployment_reachability == not_wired   (manifest or on-chain says the path is dead)
                       - design_acceptance       == match       (program-excluded / known shape)
                       - novelty                 == confirmed duplicate (dupe-screen human_review / registry hit)
                     checklist_required / flag / warn => WARN only (block-only-confident-negatives).

Block-only-confident-negatives: an UNVERIFIED finding can still reach READY. This gate forces resolution only
where it has a confident negative; the common checklist_required case WARNs, it does not block.

Never auto-rejects, never mutates finding state, never writes rejection_rules.jsonl. It blocks the *command*
so a human resolves before submitting — the human has final say.

Override: AUDITWATCH_PRECISION_OVERRIDE=1 forces exit 0 even in submission mode.
Writes output/precision_gate.json.

Usage: python scripts/precision_gate.py [--mode eval|submission] [--quiet]
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

HIGH = {"high", "critical"}
# dupe-screen registry overlap >= this is treated as a confident duplicate even below the 0.85 similarity bar
REGISTRY_DUP_SCORE = 0.7


def _sev(s: str) -> str:
    return (s or "").split(".")[0].split()[0].lower() if s else ""


def _load(p: Path, default):
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return default


def _severity_map() -> dict[str, str]:
    """finding_id -> severity, preferring the canonical candidate record, falling back to merged_findings."""
    out: dict[str, str] = {}
    merged = _load(audit_path("output") / "merged_findings.json", {})
    findings = merged.get("findings", []) if isinstance(merged, dict) else (merged or [])
    for f in findings:
        if f.get("id"):
            out[f["id"]] = _sev(f.get("severity", ""))
    cdir = audit_path("output") / "candidates"
    if cdir.is_dir():
        for cp in cdir.glob("*.json"):
            c = _load(cp, {})
            fid = c.get("id")
            if fid:
                out[fid] = _sev((c.get("classification") or {}).get("severity", out.get(fid, "")))
    return out


def _ready_ids() -> set[str] | None:
    """The READY-bound population (canonical state == 'ready'). None if no candidate records exist —
    callers then fall back to severity alone (eval is advisory; submission expects the full pipeline ran)."""
    cdir = audit_path("output") / "candidates"
    if not cdir.is_dir():
        return None
    ready = set()
    for cp in cdir.glob("*.json"):
        c = _load(cp, {})
        if c.get("state") == "ready" and c.get("id"):
            ready.add(c["id"])
    return ready


def _dupe_map() -> dict[str, dict]:
    out: dict[str, dict] = {}
    p = audit_path("data/triage") / "dupe_screen_results.jsonl"
    try:
        for line in p.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r.get("finding_id"):
                out[r["finding_id"]] = r
    except (OSError, json.JSONDecodeError):
        pass
    return out


def _confident_negatives(srisk: dict, dupe: dict | None) -> list[dict]:
    """The confident-negative axes for one finding (empty => nothing blocks)."""
    neg = []
    reach = srisk.get("deployment_reachability_risk", {}) or {}
    design = srisk.get("design_acceptance_risk", {}) or {}
    nov = srisk.get("novelty_risk", {}) or {}
    if reach.get("level") == "not_wired":
        neg.append({"axis": "deployment_reachability", "reason": reach.get("rationale", "not wired in live deployment")})
    if design.get("level") == "match":
        neg.append({"axis": "design_acceptance",
                    "reason": f"matches '{design.get('name', design.get('pattern', '?'))}' "
                              f"({design.get('outcome_provenance', '')})".strip()})
    # novelty: a confident duplicate comes from the dupe-screen (KB/Immunefi/registry), not the advisory checklist.
    if dupe:
        if dupe.get("action") == "human_review":
            neg.append({"axis": "novelty", "reason": "dupe-screen: similarity >= 0.85 to a known public report"})
        elif dupe.get("registry_match") and float(dupe.get("registry_score") or 0) >= REGISTRY_DUP_SCORE:
            neg.append({"axis": "novelty",
                        "reason": f"duplicate registry overlap with {dupe['registry_match']} "
                                  f"(score {dupe.get('registry_score')})"})
    return neg


def _soft_flags(srisk: dict, dupe: dict | None) -> list[str]:
    """Axes that WARN (need a human checklist) but never block."""
    out = []
    reach = (srisk.get("deployment_reachability_risk", {}) or {}).get("level")
    nov = (srisk.get("novelty_risk", {}) or {}).get("level")
    if reach in ("flag", "checklist_required"):
        out.append(f"deployment_reachability:{reach}")
    if nov == "checklist_required":
        out.append("novelty:checklist_required")
    if dupe and dupe.get("action") == "warn":
        out.append("novelty:warn")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["eval", "submission"], default="eval")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    srisk_doc = _load(audit_path("output") / "submission_risk.json", None)
    if not isinstance(srisk_doc, dict):
        raise SystemExit("[precision_gate] submission_risk.json missing — run submission_risk_audit.py first.")
    srisk_by_id = {r.get("finding_id"): r for r in srisk_doc.get("findings", []) if r.get("finding_id")}

    sev = _severity_map()
    ready = _ready_ids()
    dupe = _dupe_map()

    would_block, warnings = [], []
    for fid, r in srisk_by_id.items():
        s = sev.get(fid, "")
        # eligible for a hard-fail decision: High/Critical AND (READY per canonical record, or no records on disk)
        eligible = s in HIGH and (ready is None or fid in ready)
        negs = _confident_negatives(r, dupe.get(fid))
        flags = _soft_flags(r, dupe.get(fid))
        if eligible and negs:
            would_block.append({"finding_id": fid, "severity": s, "axes": negs})
        elif flags or (negs and not eligible):
            warnings.append({"finding_id": fid, "severity": s,
                             "soft_flags": flags,
                             "advisory_negatives": negs if not eligible else []})

    override = os.environ.get("AUDITWATCH_PRECISION_OVERRIDE") == "1"
    blocking = would_block if args.mode == "submission" else []
    blocked = (args.mode == "submission" and bool(blocking) and not override)
    ts = datetime.now(timezone.utc).isoformat()
    out = {"schema": "precision_gate/v1", "generated_at": ts, "mode": args.mode,
           "total": len(srisk_by_id), "blocking": blocking, "warnings": warnings,
           "would_block": would_block, "blocked": blocked, "override": override}
    (audit_path("output") / "precision_gate.json").write_text(json.dumps(out, indent=2) + "\n")

    if not args.quiet:
        verdict = "BLOCK" if blocked else "PASS"
        print(f"Precision gate ({args.mode}): {verdict}")
        print(f"  findings {len(srisk_by_id)} · confident-negative {len(would_block)} · warnings {len(warnings)}")
        for b in would_block[:10]:
            axes = ", ".join(a["axis"] for a in b["axes"])
            print(f"  {'BLOCK' if args.mode == 'submission' else 'WOULD-BLOCK'} {b['finding_id']} "
                  f"[{b['severity']}] → {axes}")
        if args.mode == "eval":
            print("  (eval mode: advisory only — does not block the eval candidate set)")
    return 1 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
