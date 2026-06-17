#!/usr/bin/env python3
"""
init_coverage_dispositions.py — Initialize/refresh output/coverage_dispositions.json (no LLM).

One disposition per manifest item. In-scope items start `unassigned`; out-of-scope items are
pre-set to `deferred_out_of_scope` carrying the manifest's scope_reason (so the gate never demands
review of mocks/tests/interfaces). Idempotent: existing dispositions are PRESERVED; only new manifest
ids are added, and stale ids (no longer in the manifest) are dropped with a note.

Usage:
    python scripts/init_coverage_dispositions.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402

ALLOWED = {"unassigned", "assigned", "examined", "cleared", "finding", "deferred_out_of_scope"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> int:
    man_path = audit_path("output") / "coverage_manifest.json"
    if not man_path.exists():
        raise SystemExit("[init_coverage_dispositions] coverage_manifest.json missing — "
                         "run scripts/build_coverage_manifest.py first.")
    manifest = json.loads(man_path.read_text())
    items = manifest.get("items", [])

    disp_path = audit_path("output") / "coverage_dispositions.json"
    existing: dict[str, dict] = {}
    if disp_path.exists():
        try:
            data = json.loads(disp_path.read_text())
            for d in data.get("dispositions", data if isinstance(data, list) else []):
                if d.get("manifest_id"):
                    existing[d["manifest_id"]] = d
        except (json.JSONDecodeError, OSError):
            existing = {}

    out: list[dict] = []
    manifest_ids = set()
    added = preserved = 0
    for it in items:
        mid = it["id"]
        manifest_ids.add(mid)
        if mid in existing:
            out.append(existing[mid]); preserved += 1
            continue
        if not it.get("in_scope", True):
            status = "deferred_out_of_scope"
            reason = it.get("scope_reason", "out of scope")
        else:
            status = "unassigned"
            reason = None
        out.append({
            "manifest_id": mid,
            "status": status,
            "assigned_pass": None,
            "assigned_agent": None,
            "evidence": [],
            "finding_refs": [],
            "clear_reason": reason if status == "deferred_out_of_scope" else None,
            "scope_reason": reason if status == "deferred_out_of_scope" else None,
            # P245 #3 (additive, optional): out-of-scope items satisfy read-completeness as NOT_IN_SCOPE;
            # in-scope items start with no read_state (= not yet read in full). The read-completeness
            # gate only consults this when explicitly enforced (default-off), so this never changes
            # current behavior.
            "read_state": "NOT_IN_SCOPE" if status == "deferred_out_of_scope" else None,
            "updated_at": _now(),
        })
        added += 1

    dropped = [mid for mid in existing if mid not in manifest_ids]
    disp_path.write_text(json.dumps({
        "generated_at": _now(),
        "manifest": "output/coverage_manifest.json",
        "dispositions": out,
    }, indent=2))

    from collections import Counter
    by_status = dict(Counter(d["status"] for d in out))
    print(f"[ok] coverage dispositions → {disp_path}")
    print(f"     total: {len(out)} (added {added}, preserved {preserved}, dropped-stale {len(dropped)})")
    print(f"     by status: {by_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
