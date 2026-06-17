#!/usr/bin/env python3
"""deep_pass_schedule_research.py — Phase-22 RESEARCH-ONLY wrapper around the FROZEN deep_pass_schedule.py.

Guardrail (Phase 22): the frozen scheduler hardcodes deep_pass/candidate_queue.json and cannot read an alternate
frozen queue (e.g. candidate_queue_bridge_recall.json) without mutating a frozen artifact. This wrapper adds
explicit --queue <path> and --out-dir <path> so BOTH A/B arms can be scheduled from their frozen queues into a
SEPARATE output directory. It REUSES the frozen scheduler's exact `_expand_callees` (mandatory recursive callee
expansion) + `_function_body` + manifest callee resolution, so this is genuinely scheduler-EQUIVALENT — not a
substituted analysis path. The frozen deep_pass_schedule.py is imported, never edited.

  is_gate:false  research_only:true  routes_in_production:false  routed_manifest_ids:[]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
import deep_pass_schedule as frozen  # reuse frozen _expand_callees / _function_body / _load  # noqa: E402

FLAGS = {"is_gate": False, "research_only": True, "routes_in_production": False, "routed_manifest_ids": []}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--queue", required=True, help="explicit frozen queue json (OLD or BRIDGE_RECALL)")
    ap.add_argument("--out-dir", required=True, help="separate output dir for _schedule/ + trace_ledger.json")
    ap.add_argument("--manifest", help="coverage_manifest.json (default: active audit output)")
    ap.add_argument("--budget", type=int, default=999, help="max untraced candidates scheduled this run")
    ap.add_argument("--depth", type=int, default=2, help="recursive callee-expansion depth")
    ap.add_argument("--reconcile", help="decisions.json: mark candidates traced (callee-complete)")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--no-source", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    man_path = Path(args.manifest) if args.manifest else (audit_path("output") / "coverage_manifest.json")
    items = frozen._load(man_path).get("items", [])
    by_id = {it["id"]: it for it in items}
    by_name = {it.get("name"): it for it in items if it.get("kind") in ("function", "initializer")}
    queue = frozen._load(Path(args.queue)).get("queue", [])
    ledger_path = out_dir / "trace_ledger.json"
    traced = set(frozen._load(ledger_path).get("traced", []))

    if args.reconcile:
        decs = frozen._load(Path(args.reconcile)).get("decisions", [])
        newly = []
        for d in decs:
            if not d.get("function_analyzed"):
                continue
            ca, an = set(d.get("callees_available") or []), set(d.get("callees_analyzed") or [])
            if ca <= an and d.get("manifest_id") not in traced:
                traced.add(d.get("manifest_id")); newly.append(d.get("manifest_id"))
        ledger_path.write_text(json.dumps({"traced": sorted(traced)}, indent=2))
        if not args.quiet:
            print(f"[reconcile] +{len(newly)} traced; total {len(traced)}/{len(queue)}")
        return 0

    untraced = [q for q in queue if q.get("manifest_id") not in traced]
    if args.status:
        print(f"[status] queue {len(queue)} · traced {len(traced)} · untraced {len(untraced)}")
        return 0

    sched_dir = out_dir / "_schedule"
    sched_dir.mkdir(parents=True, exist_ok=True)
    for old in sched_dir.glob("sched_*.json"):
        old.unlink()
    use_source = not args.no_source
    scheduled = []
    for i, q in enumerate(untraced[:args.budget]):
        it = by_id.get(q.get("manifest_id"))
        if not it:
            continue
        sp = it.get("source_span", {})
        body = frozen._function_body(it.get("file", ""), sp.get("start_line"), use_source)
        callees = frozen._expand_callees(it, by_name, by_id, use_source, args.depth, {it.get("id")})
        sid = f"sched_{i:04d}"
        (sched_dir / f"{sid}.json").write_text(json.dumps({
            "sched_id": sid, "manifest_id": it.get("id"), "contract": it.get("contract"),
            "function": it.get("name"), "file_line_refs": f"{it.get('file','')}:{sp.get('start_line','')}",
            "function_body": body, "callees_available": [c["name"] for c in callees], "callees": callees,
            "trace_required": ["function_analyzed", "callees_analyzed (ALL)", "state_vars_traced or external_calls_traced", "decision_made"],
        }, indent=2))
        scheduled.append({"sched_id": sid, "manifest_id": it.get("id"), "contract": it.get("contract"),
                          "function": it.get("name"), "n_callees": len(callees)})
    (sched_dir / "schedule.json").write_text(json.dumps({
        **FLAGS, "scheduler_equivalent_of": "deep_pass_schedule.py (imported, unedited)",
        "queue": str(args.queue), "queue_size": len(queue), "traced": len(traced), "untraced": len(untraced),
        "scheduled_this_run": len(scheduled), "budget": args.budget, "depth": args.depth,
        "untraced_remaining_after": max(0, len(untraced) - len(scheduled)), "scheduled": scheduled,
    }, indent=2))
    if not args.quiet:
        print(f"[schedule:research] queue {len(queue)} → scheduled {len(scheduled)} "
              f"(budget {args.budget}, depth {args.depth}) → {sched_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
