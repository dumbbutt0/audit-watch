#!/usr/bin/env python3
"""
coverage_sweep_prepare.py — Bundle un-dispositioned in-scope manifest items for the /coverage-sweep
skill (deterministic, no LLM).

Selects in-scope items whose disposition is still `unassigned`/`assigned` (i.e. not yet examined,
cleared, finding, or deferred), groups them by file (lowest attack-surface-score first — the cheap
sweep targets the long tail the deep specialists skipped), and writes a per-file bundle plus an index.
The skill reads source itself; bundles stay lightweight.

Usage:
    python scripts/coverage_sweep_prepare.py [--max-items N]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-items", type=int, default=0, help="0 = all pending in-scope items")
    ap.add_argument("--order", choices=["low", "high"], default="low",
                    help="low = cheap tail first (default); high = high-attack-surface first")
    ap.add_argument("--min-score", type=int, default=0, help="only items with attack_surface_score >= N")
    ap.add_argument("--tags", default="", help="comma-separated; include items having any of these tags")
    args = ap.parse_args()

    man_path = audit_path("output") / "coverage_manifest.json"
    disp_path = audit_path("output") / "coverage_dispositions.json"
    if not man_path.exists() or not disp_path.exists():
        raise SystemExit("[coverage_sweep_prepare] manifest or dispositions missing — build/init first.")
    items = {i["id"]: i for i in json.loads(man_path.read_text()).get("items", [])}
    disp = {d["manifest_id"]: d for d in json.loads(disp_path.read_text()).get("dispositions", [])}

    want_tags = {t.strip() for t in (args.tags or "").split(",") if t.strip()}
    # Only 'unassigned' items are sweepable. 'assigned' means already routed (needs_deep_pass) —
    # excluding it keeps iterative batches moving forward instead of re-sweeping the deep-pass queue.
    pending = [items[mid] for mid in items
               if items[mid].get("in_scope", True)
               and disp.get(mid, {}).get("status", "unassigned") == "unassigned"
               and items[mid].get("attack_surface_score", 0) >= args.min_score
               and (not want_tags or want_tags & set(items[mid].get("tags", [])))]
    # default low-score first (cheap tail); --order high targets high-surface items first.
    reverse = (args.order == "high")
    pending.sort(key=lambda it: (it.get("attack_surface_score", 0), it["file"]), reverse=reverse)
    if args.max_items:
        pending = pending[:args.max_items]

    by_file: dict[str, list[dict]] = defaultdict(list)
    for it in pending:
        by_file[it["file"]].append({
            "manifest_id": it["id"], "kind": it["kind"], "name": it["name"],
            "contract": it.get("contract"), "signature": it.get("signature", ""),
            "visibility": it.get("visibility", ""), "tags": it.get("tags", []),
            "attack_surface_score": it.get("attack_surface_score", 0),
            "source_span": it.get("source_span", {}),
        })

    bundle_dir = audit_path("output") / "coverage_sweep" / "_bundles"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    index = []
    for i, (file, its) in enumerate(sorted(by_file.items())):
        bid = f"sweep_{i:04d}"
        (bundle_dir / f"{bid}.json").write_text(json.dumps({
            "bundle_id": bid, "file": file, "item_count": len(its), "items": its,
        }, indent=2))
        index.append({"bundle_id": bid, "file": file, "item_count": len(its)})
    (bundle_dir / "index.json").write_text(json.dumps({
        "total_pending_items": len(pending), "bundles": index,
        "instructions": ("For each item read the file's source span, then emit one disposition per "
                         "item in data/coverage_sweep/_decisions.json: cleared|finding|needs_deep_pass|"
                         "deferred_out_of_scope. A 'cleared' MUST carry evidence (file:line or span) and "
                         "a one-line reason naming the guard/invariant/no-attacker-path. Then run "
                         "python scripts/coverage_sweep_write.py."),
    }, indent=2))

    print(f"[ok] coverage-sweep bundles → {bundle_dir}")
    print(f"     {len(pending)} pending in-scope items across {len(by_file)} files")
    print("     Next: run the /coverage-sweep skill, then python scripts/coverage_sweep_write.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
