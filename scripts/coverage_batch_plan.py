#!/usr/bin/env python3
"""
coverage_batch_plan.py — Deterministic batch plan for sweeping the manifest long tail (no LLM).

Groups all pending in-scope manifest items (status unassigned/assigned) into six ordered batches and
writes output/coverage_sweep/batch_plan.json with, per batch, the member manifest-ids and the exact
coverage_sweep_prepare.py command to materialize it. Each item is assigned to exactly ONE batch (first
matching group wins) so the batches partition the pending set.

Order: 1 high-score (>=threshold) · 2 constants/immutables/addresses/decimals · 3 oracle/accounting/
token/config · 4 permissioned/initializer/migration · 5 loops/dos/external_call · 6 remaining low-score.

Usage:
    python scripts/coverage_batch_plan.py
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def _threshold() -> int:
    try:
        return json.loads((ROOT / "config" / "agent_policy.json").read_text()) \
            .get("coverage_policy", {}).get("high_score_threshold", 3)
    except Exception:
        return 3


def _low_score_plan(items: dict, disp: dict, thr: int) -> int:
    """Batch plan for the score<threshold unassigned long tail, grouped by review difficulty then
    contract (cap 40/packet). Written to output/coverage_sweep/low_score_batch_plan.json."""
    pending = [items[mid] for mid in items
               if items[mid].get("in_scope", True)
               and disp.get(mid, {}).get("status", "unassigned") == "unassigned"
               and items[mid].get("attack_surface_score", 0) < thr]

    def group_of(it):
        mut = it.get("mutability")
        vis = it.get("visibility")
        if it["kind"] == "function" and mut in ("view", "pure"):
            return "1_readonly_view_pure"
        if vis in ("internal", "private"):
            return "2_statechanging_internal_private"
        if vis in ("external", "public"):
            return "3_statechanging_external_public"
        return "4_misc"

    GROUP_CMD = {
        "1_readonly_view_pure": "python scripts/coverage_sweep_prepare.py --order low --max-items 150",
        "2_statechanging_internal_private": "python scripts/coverage_sweep_prepare.py --order low --max-items 150",
        "3_statechanging_external_public": "python scripts/coverage_sweep_prepare.py --order low --max-items 150",
        "4_misc": "python scripts/coverage_sweep_prepare.py --order low --max-items 150",
    }
    CAP = 40
    buckets: dict[tuple, list[dict]] = defaultdict(list)
    for it in pending:
        buckets[(group_of(it), it.get("contract") or "?")].append(it)

    packets = []
    for (group, contract), its in buckets.items():
        for ci in range(0, len(its), CAP):
            chunk = its[ci:ci + CAP]
            suffix = f"-{ci // CAP + 1}" if len(its) > CAP else ""
            packets.append({
                "packet_id": f"LSP-{group}-{contract}{suffix}",
                "group": group, "contract": contract,
                "item_count": len(chunk),
                "files": sorted({i["file"] for i in chunk}),
                "manifest_ids": sorted(i["id"] for i in chunk),
                "prepare_command": GROUP_CMD[group],
            })
    packets.sort(key=lambda p: (p["group"], -p["item_count"]))
    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "low_score", "high_score_threshold": thr,
        "total_pending_low_score": len(pending),
        "packets": packets,
        "note": "Low-score (score<threshold) unassigned long tail. Sweep in waves of ~150 with "
                "`--order low`; read each item's span — view/pure clear cheaply with evidence+reason, "
                "escalate non-trivial getters to needs_deep_pass. Then coverage_sweep_write.py.",
    }
    bp = audit_path("output") / "coverage_sweep" / "low_score_batch_plan.json"
    bp.parent.mkdir(parents=True, exist_ok=True)
    bp.write_text(json.dumps(out, indent=2))
    from collections import Counter
    gc = Counter(group_of(it) for it in pending)
    print(f"[ok] low-score batch plan → {bp}")
    print(f"     pending low-score: {len(pending)} across {len(packets)} packets")
    for g in sorted(gc):
        print(f"     {g}: {gc[g]}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Coverage sweep batch plan (deterministic, no LLM).")
    ap.add_argument("--low-score", action="store_true",
                    help="Plan the score<threshold unassigned long tail → low_score_batch_plan.json")
    args = ap.parse_args()

    man_path = audit_path("output") / "coverage_manifest.json"
    disp_path = audit_path("output") / "coverage_dispositions.json"
    if not man_path.exists() or not disp_path.exists():
        raise SystemExit("[coverage_batch_plan] manifest or dispositions missing — build/init first.")
    items = {i["id"]: i for i in json.loads(man_path.read_text()).get("items", [])}
    disp = {d["manifest_id"]: d for d in json.loads(disp_path.read_text()).get("dispositions", [])}
    thr = _threshold()

    if args.low_score:
        return _low_score_plan(items, disp, thr)

    pending = [items[mid] for mid in items
               if items[mid].get("in_scope", True)
               and disp.get(mid, {}).get("status", "unassigned") in ("unassigned", "assigned")]

    def has(it, *tags):
        return bool(set(tags) & set(it.get("tags", [])))

    batches = [
        {"name": "1_high_score", "desc": f"high attack-surface (score>={thr})",
         "cmd": f"python scripts/coverage_sweep_prepare.py --order high --min-score {thr}",
         "match": lambda it: it.get("attack_surface_score", 0) >= thr},
        {"name": "2_constants_addresses", "desc": "constants / immutables / addresses / decimals",
         "cmd": "python scripts/coverage_sweep_prepare.py --tags constant,decimals",
         "match": lambda it: it["kind"] in ("constant", "immutable", "address") or has(it, "decimals")},
        {"name": "3_oracle_accounting_token_config", "desc": "oracle / accounting / token / config tags",
         "cmd": "python scripts/coverage_sweep_prepare.py --tags oracle,accounting,token,config",
         "match": lambda it: has(it, "oracle", "accounting", "token", "config")},
        {"name": "4_permissioned_init_migration", "desc": "permissioned / initializer / migration",
         "cmd": "python scripts/coverage_sweep_prepare.py --tags permissions,migration",
         "match": lambda it: it["kind"] in ("initializer", "constructor") or has(it, "permissions", "migration")},
        {"name": "5_loops_dos_external", "desc": "loops / dos / external calls",
         "cmd": "python scripts/coverage_sweep_prepare.py --tags loop,dos,external_call",
         "match": lambda it: has(it, "loop", "dos", "external_call") or it.get("external_calls")},
        {"name": "6_remaining_low_score", "desc": "remaining low-score items",
         "cmd": "python scripts/coverage_sweep_prepare.py --order low",
         "match": lambda it: True},
    ]

    assigned: set[str] = set()
    plan_batches = []
    for b in batches:
        ids = [it["id"] for it in pending if it["id"] not in assigned and b["match"](it)]
        assigned.update(ids)
        plan_batches.append({"name": b["name"], "description": b["desc"],
                             "prepare_command": b["cmd"], "item_count": len(ids),
                             "manifest_ids": ids})

    total = len(pending)
    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "high_score_threshold": thr,
        "total_pending_in_scope": total,
        "assigned_across_batches": len(assigned),
        "batches": plan_batches,
        "note": "Batches partition the pending in-scope set (first match wins). Run a batch with its "
                "prepare_command (optionally add --max-items N for a calibration slice), then the "
                "/coverage-sweep skill, then python scripts/coverage_sweep_write.py.",
    }
    bp = audit_path("output") / "coverage_sweep" / "batch_plan.json"
    bp.parent.mkdir(parents=True, exist_ok=True)
    bp.write_text(json.dumps(out, indent=2))

    print(f"[ok] batch plan → {bp}")
    print(f"     pending in-scope: {total} (partitioned across {len(plan_batches)} batches)")
    for b in plan_batches:
        print(f"     {b['name']}: {b['item_count']}")
    assert len(assigned) == total, "batch partition must cover all pending items"
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
