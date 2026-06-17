#!/usr/bin/env python3
"""
replay_miss_class.py — replay the Revert Lend miss-classes against the NEW adversarial-review validators
(spec checklists + waiver risk discipline), READ-ONLY on the frozen eval.

It loads the frozen snapshot artifacts (never mutating them) and runs the new validator LOGIC in-process to
report which frozen `cleared` dispositions would now route to needs_deep_pass (incomplete spec checklist),
and which frozen waived clusters held high-risk items that the new discipline would block.

Run: python audits/revert-lend-2024-03-strict-eval/replay/replay_miss_class.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

AUDIT = Path(__file__).resolve().parent.parent
ROOT = AUDIT.parent.parent
SNAP = AUDIT / "output" / "pre_answer_key_snapshot"
REPLAY = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))

import spec_checklist_utils as scu  # noqa: E402
import waiver_utils as wu  # noqa: E402


def _find(suffix: str) -> Path | None:
    if not SNAP.exists():
        return None
    for p in SNAP.iterdir():
        if p.name.endswith(suffix):
            return p
    return None


def _load(suffix: str) -> dict:
    p = _find(suffix)
    return json.loads(p.read_text()) if p else {}


def replay() -> dict:
    man = {i["id"]: i for i in _load("coverage_manifest.json").get("items", [])}
    disp = _load("coverage_dispositions.json").get("dispositions", [])
    waiver = _load("deep_pass_waiver.json")
    cleared = [d for d in disp if d.get("status") == "cleared"]

    spec_route = []
    for d in cleared:
        cls = scu.classify(d, man.get(d["manifest_id"]))
        if cls["status"] == scu.ROUTED_STATUS:
            spec_route.append({"manifest_id": d["manifest_id"], "surface": cls["surface"]})

    # which cluster-waived items were actually high-risk (now require a per-sink waiver / block)
    cluster_ids = {w.get("cluster_id") for w in (waiver.get("waivers") or []) if w.get("cluster_id")}
    queue = _load("deep_pass_queue.json")
    high_risk_in_cluster_waivers = []
    for c in queue.get("clusters", []):
        if c.get("cluster_id") in cluster_ids:
            for mid in c.get("item_ids", []):
                rc = wu.risk_class(man.get(mid, {}))
                if rc != "none":
                    high_risk_in_cluster_waivers.append({"manifest_id": mid, "risk_class": rc,
                                                         "cluster_id": c["cluster_id"]})
    return {
        "cleared_count": len(cleared),
        "spec_checklist_would_route": spec_route,
        "high_risk_items_under_cluster_waivers": high_risk_in_cluster_waivers,
        "findings_minted_by_validators": 0,    # validators only route/block
    }


def main() -> int:
    if not SNAP.exists():
        print(f"frozen snapshot not present: {SNAP}", file=sys.stderr)
        return 1
    res = replay()
    REPLAY.mkdir(exist_ok=True)
    (REPLAY / "miss_class_report.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
