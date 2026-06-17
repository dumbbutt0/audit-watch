#!/usr/bin/env python3
"""
deep_pass_schedule.py — Phase-19 RESEARCH-ONLY queue scheduler (un-wired, no gate, no routing).

Phase 19 showed the reasoning pass deep-reads only ~20% of a large queue, so in-queue bugs are missed before
reasoning engages them. This scheduler turns the frozen sampler's candidate_queue.json into an EXHAUSTIVE,
BUDGETED, RESUMABLE work-list: one candidate per scheduled bundle, MANDATORY recursive callee expansion (so no
callee is silently skipped), a budget cap per run, and a resumable trace ledger so a paused run continues
without re-tracing. It does NOT edit deep_pass_prepare.py / deep_pass_write.py / the sampler — it reuses
_function_body for bodies and the manifest for callee resolution.

  is_gate:false · research_only:true · routes_in_production:false

Usage:
  python scripts/deep_pass_schedule.py [--budget 15] [--depth 2] [--manifest <p>] [--quiet]
  python scripts/deep_pass_schedule.py --reconcile <decisions.json>   # mark traced candidates in the ledger
  python scripts/deep_pass_schedule.py --status                       # report scheduled/traced/untraced
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
from sibling_function_parity_audit import _function_body  # noqa: E402

_CALL_RE = re.compile(r"(?<![\w.])([A-Za-z_]\w*)\s*\(")
_SKIP = {"require", "assert", "emit", "if", "for", "while", "return", "revert", "abi", "address",
         "uint256", "keccak256", "new"}


def _load(p: Path):
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _expand_callees(item, by_name, by_id, use_source, depth, seen):
    """Recursive mandatory callee expansion: return [{name,contract,file_line,body}] up to `depth`."""
    out = []
    sp = item.get("source_span", {})
    body = _function_body(item.get("file", ""), sp.get("start_line"), use_source)
    if depth <= 0:
        return out
    for m in _CALL_RE.finditer(body or ""):
        nm = m.group(1)
        if nm in _SKIP or nm == item.get("name"):
            continue
        tgt = by_name.get(nm)
        if not tgt or tgt.get("id") in seen:
            continue
        seen.add(tgt.get("id"))
        csp = tgt.get("source_span", {})
        cbody = _function_body(tgt.get("file", ""), csp.get("start_line"), use_source)
        if cbody:
            out.append({"name": nm, "contract": tgt.get("contract"),
                        "file_line": f"{tgt.get('file','')}:{csp.get('start_line','')}", "body": cbody})
            out += _expand_callees(tgt, by_name, by_id, use_source, depth - 1, seen)  # recurse
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest")
    ap.add_argument("--budget", type=int, default=15, help="max untraced candidates scheduled this run")
    ap.add_argument("--depth", type=int, default=2, help="recursive callee-expansion depth")
    ap.add_argument("--reconcile", help="decisions.json: mark candidates with function_analyzed as traced")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--no-source", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    out_dir = audit_path("output")
    man_path = Path(args.manifest) if args.manifest else out_dir / "coverage_manifest.json"
    items = _load(man_path).get("items", [])
    by_id = {it["id"]: it for it in items}
    by_name = {it.get("name"): it for it in items if it.get("kind") in ("function", "initializer")}
    queue = _load(out_dir / "deep_pass" / "candidate_queue.json").get("queue", [])
    ledger_path = out_dir / "deep_pass" / "trace_ledger.json"
    traced = set(_load(ledger_path).get("traced", []))

    # --reconcile: a candidate counts as traced when its trace record has function_analyzed AND every available
    # callee was analyzed (mandatory callee expansion enforced).
    if args.reconcile:
        decs = _load(Path(args.reconcile)).get("decisions", [])
        newly = []
        for d in decs:
            if not d.get("function_analyzed"):
                continue
            ca = set(d.get("callees_available") or [])
            an = set(d.get("callees_analyzed") or [])
            if ca <= an and d.get("manifest_id") not in traced:
                traced.add(d.get("manifest_id")); newly.append(d.get("manifest_id"))
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        ledger_path.write_text(json.dumps({"traced": sorted(traced)}, indent=2))
        if not args.quiet:
            print(f"[reconcile] +{len(newly)} traced (callee-complete); total traced {len(traced)}/{len(queue)}")
        return 0

    untraced = [q for q in queue if q.get("manifest_id") not in traced]
    if args.status:
        print(f"[status] queue {len(queue)} · traced {len(traced)} · untraced {len(untraced)}")
        for q in untraced[:20]:
            print(f"   UNTRACED {q.get('contract')}.{q.get('function')}")
        return 0

    # schedule the next `budget` untraced candidates, one bundle each, with mandatory recursive callee expansion
    sched_dir = out_dir / "deep_pass" / "_schedule"
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
        body = _function_body(it.get("file", ""), sp.get("start_line"), use_source)
        callees = _expand_callees(it, by_name, by_id, use_source, args.depth, {it.get("id")})
        sid = f"sched_{i:04d}"
        (sched_dir / f"{sid}.json").write_text(json.dumps({
            "sched_id": sid, "manifest_id": it.get("id"), "contract": it.get("contract"),
            "function": it.get("name"), "file_line_refs": f"{it.get('file','')}:{sp.get('start_line','')}",
            "function_body": body, "callees_available": [c["name"] for c in callees], "callees": callees,
            "trace_required": ["function_analyzed", "callees_analyzed (ALL)", "state_vars_traced or external_calls_traced", "decision_made"],
        }, indent=2))
        scheduled.append({"sched_id": sid, "manifest_id": it.get("id"),
                          "contract": it.get("contract"), "function": it.get("name"),
                          "n_callees": len(callees)})
    (sched_dir / "schedule.json").write_text(json.dumps({
        "is_gate": False, "research_only": True, "routes_in_production": False,
        "queue_size": len(queue), "traced": len(traced), "untraced": len(untraced),
        "scheduled_this_run": len(scheduled), "budget": args.budget, "depth": args.depth,
        "ledger": str(ledger_path), "scheduled": scheduled,
        "untraced_remaining_after": max(0, len(untraced) - len(scheduled)),
    }, indent=2))
    if not args.quiet:
        print(f"[schedule] queue {len(queue)} · traced {len(traced)} · untraced {len(untraced)} → "
              f"scheduled {len(scheduled)} (budget {args.budget}, callee-depth {args.depth})")
        print(f"     {len(untraced) - len(scheduled)} untraced remain after this run → re-run to continue "
              f"(resumable via {ledger_path.name}). RESEARCH-ONLY, un-wired.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
