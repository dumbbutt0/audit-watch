#!/usr/bin/env python3
"""
poc_fix_all.py — Batch driver: stage the whole engagement's PoC-fix queue in one pass (deterministic, no LLM).

`poc-fix <id>` handles one finding; `poc-fix-all` walks the fix-list in priority order, stages a fix session
(and a /poc-validation bundle) for every actionable finding, and writes a consolidated operator worklist. It
**stages work safely**: it never executes test commands by default and never invents forge commands; a failure
on one item is recorded and the batch continues.

Reuses poc_fix.load_context / poc_fix.process_finding.

Reads:  output/poc_validation/{fix_list,engagement_report,poc_inventory,poc_validation_results}.json
Writes: output/poc_validation/operator_worklist.json + .md  (+ per-finding fix_sessions/<id>.{json,md})
        merges worklist fields into output/dashboard/poc_validation_status.json (if present)

Usage:
    python scripts/poc_fix_all.py
      [--mode engagement|submission] [--limit N] [--actions a,b] [--severity High,Medium,Low]
      [--include-ready] [--run-collect] [--overwrite] [--json]
"""
from __future__ import annotations

import argparse
import json
import sys
from argparse import Namespace
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
import poc_validation_gate as gate  # noqa: E402  (SEV_RANK)
import poc_fix  # noqa: E402  (load_context, process_finding)


def _load_json(path: Path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return default


def batch_priority(item: dict) -> int:
    """The request's 6-level batch order."""
    r = gate.SEV_RANK.get(item.get("severity", "Unknown"), 2)
    bucket = item.get("current_bucket")
    if item.get("blocked") and r >= 3:
        return 0  # High/Critical blocked
    if item.get("blocked") and r == 2:
        return 1  # Medium blocked
    if bucket == "engagement_ready_but_not_submission_ready":
        return 2  # closest to submission-ready
    if bucket == "missing_collected_log":
        return 3
    if bucket == "missing_poc":
        return 4
    return 5      # duplicate / reject / cleanup


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["engagement", "submission"], default=None)
    ap.add_argument("--limit", type=int, default=0, help="0 = all")
    ap.add_argument("--actions", default="", help="comma-separated recommended_next_action filter")
    ap.add_argument("--severity", default="", help="comma-separated severity filter (e.g. High,Medium)")
    ap.add_argument("--include-ready", action="store_true", help="also list already submission-ready findings")
    ap.add_argument("--run-collect", action="store_true",
                    help="execute a collect ONLY when a command is already present (never invents one)")
    ap.add_argument("--overwrite", action="store_true", help="re-stage sessions that already exist")
    ap.add_argument("--json", action="store_true", dest="as_json")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    pv = audit_path("output", "poc_validation")
    er, inv_by, vr_by, mf_by, fix_by, fl, mode = poc_fix.load_context(pv, args.mode)
    items = list((fl or {}).get("ordered_items", []))

    # filters
    action_filter = {a.strip() for a in args.actions.split(",") if a.strip()}
    sev_filter = {s.strip().title() for s in args.severity.split(",") if s.strip()}
    if action_filter:
        items = [it for it in items if it.get("recommended_next_action") in action_filter]
    if sev_filter:
        items = [it for it in items if (it.get("severity") or "").title() in sev_filter]

    # priority order
    items.sort(key=lambda it: (batch_priority(it), -gate.SEV_RANK.get(it.get("severity", "Unknown"), 2),
                               -it.get("proof_score", 0), it.get("finding_id", "")))
    if args.limit:
        items = items[:args.limit]

    sess_dir = pv / "fix_sessions"
    worklist, staged, skipped, failed = [], 0, 0, 0
    rank = 0
    for it in items:
        fid = it["finding_id"]
        rank += 1
        sess_json = sess_dir / f"{fid}.json"
        status, session = "staged", None
        try:
            if sess_json.exists() and not args.overwrite:
                session = _load_json(sess_json) or {}
                status = "skipped"
            else:
                # synthesize per-finding args: never invent a collect command (only stage templates).
                fargs = Namespace(collect_command=None, test_file=None, test_name=None,
                                  overwrite=True, as_json=False)
                session = poc_fix.process_finding(fid, it, inv_by.get(fid, {}), vr_by.get(fid, {}),
                                                  mf_by.get(fid, {}), fargs, mode)
                status = "staged"
        except Exception as e:  # record + continue (never abort the batch)
            status = "failed"
            session = {"error": f"{type(e).__name__}: {e}"}
            failed += 1
        if status == "staged":
            staged += 1
        elif status == "skipped":
            skipped += 1
        worklist.append({
            "rank": rank,
            "finding_id": fid,
            "title": it.get("title", ""),
            "severity": it.get("severity"),
            "current_bucket": it.get("current_bucket"),
            "recommended_next_action": it.get("recommended_next_action"),
            "why_blocked": it.get("why_blocked"),
            "shortest_next_step": it.get("shortest_next_step"),
            "fix_session_json": str((sess_dir / f"{fid}.json").relative_to(audit_path("."))) if status != "failed" else None,
            "fix_session_md": str((sess_dir / f"{fid}.md").relative_to(audit_path("."))) if status != "failed" else None,
            "prepared_bundle_path": (session or {}).get("prepared_bundle_path"),
            "generated_commands": (session or {}).get("generated_commands", []),
            "manual_checklist": (session or {}).get("checklist", []),
            "ready_for_poc_validation": bool((session or {}).get("prepared_bundle_path")),
            "status": status,
        })

    if args.include_ready:
        ready_ids = {w["finding_id"] for w in worklist}
        for f in er.get("findings", []):
            if f.get("bucket") == "submission_ready" and f["finding_id"] not in ready_ids:
                rank += 1
                worklist.append({
                    "rank": rank, "finding_id": f["finding_id"], "title": f.get("title", ""),
                    "severity": f.get("severity"), "current_bucket": "submission_ready",
                    "recommended_next_action": "none", "why_blocked": None,
                    "shortest_next_step": "Already submission-ready — submit as-is.",
                    "fix_session_json": None, "fix_session_md": None, "prepared_bundle_path": None,
                    "generated_commands": [], "manual_checklist": [], "ready_for_poc_validation": False,
                    "status": "ready",
                })

    next_batch_actions = Counter(w["recommended_next_action"] for w in worklist
                                 if w["recommended_next_action"] not in (None, "none")).most_common(5)
    generated_at = datetime.now(timezone.utc).isoformat()
    out = {"generated_at": generated_at, "mode": mode, "total": len(worklist),
           "staged": staged, "skipped": skipped, "failed": failed,
           "next_batch_actions": next_batch_actions, "items": worklist}
    (pv / "operator_worklist.json").write_text(json.dumps(out, indent=2))

    # markdown: priority table + checklist grouped by action then severity
    md = [f"# PoC Operator Worklist ({mode} mode)", "", f"_generated {generated_at}_", "",
          f"**{len(worklist)} item(s)** · staged {staged} · skipped {skipped} · failed {failed}", "",
          "| Rank | Finding | Sev | Bucket | Next action | Ready for /poc-validation |",
          "|---|---|---|---|---|---|"]
    for w in worklist:
        md.append(f"| {w['rank']} | {w['finding_id']} | {w['severity']} | {w['current_bucket']} | "
                  f"{w['recommended_next_action']} | {'yes' if w['ready_for_poc_validation'] else 'no'} |")
    md += ["", "## Checklist by action", ""]
    by_action: dict[str, list] = {}
    for w in worklist:
        by_action.setdefault(w["recommended_next_action"] or "none", []).append(w)
    for action, ws in by_action.items():
        md.append(f"### {action} ({len(ws)})")
        md.append("")
        for w in sorted(ws, key=lambda x: -gate.SEV_RANK.get(x.get("severity", "Unknown"), 2)):
            ready = " · **bundle ready → /poc-validation**" if w["ready_for_poc_validation"] else ""
            md.append(f"- [ ] **{w['finding_id']}** ({w['severity']}) — {w['shortest_next_step']}{ready}")
            if w["status"] == "failed":
                md.append(f"      ⚠ failed to stage")
        md.append("")
    (pv / "operator_worklist.md").write_text("\n".join(md) + "\n")

    # merge worklist fields into the dashboard artifact (if it exists) — never create a dependency
    dash_path = audit_path("output", "dashboard", "poc_validation_status.json")
    dash = _load_json(dash_path)
    if isinstance(dash, dict):
        dash["operator_worklist_path"] = str((pv / "operator_worklist.md").relative_to(audit_path(".")))
        dash["operator_worklist_count"] = len(worklist)
        dash["next_batch_actions"] = next_batch_actions
        dash_path.write_text(json.dumps(dash, indent=2))

    if args.as_json:
        print(json.dumps(out, indent=2))
    elif not args.quiet:
        print(f"PoC fix-all ({mode}): {len(worklist)} item(s) · staged {staged} · skipped {skipped} · failed {failed}")
        for w in worklist[:10]:
            print(f"  #{w['rank']:>2} {w['finding_id']} ({w['severity']}) → {w['recommended_next_action']}"
                  f"{'  [bundle ready]' if w['ready_for_poc_validation'] else ''}  [{w['status']}]")
        print(f"  → {pv / 'operator_worklist.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
