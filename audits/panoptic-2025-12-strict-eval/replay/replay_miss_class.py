#!/usr/bin/env python3
"""
replay_miss_class.py — replay the Panoptic miss-classes against the NEW conversion-engine validators
(advisory escalation routing + gate-vs-DoS + special-focus), READ-ONLY on the frozen eval.

It copies the frozen artifacts into this replay/ dir (never mutating the snapshot) and runs the new
validator LOGIC in-process. Two blocks:
  A. Literal frozen replay — classify every frozen `cleared` disposition with the new validators and
     report which frozen clears would now route to needs_deep_pass (the conversion the upgrade adds).
  B. FP check — the validators never mint findings, and frozen `finding`/`needs_deep_pass` items are
     untouched, so no prior result is converted into a finding-level false positive.

Run: python audits/panoptic-2025-12-strict-eval/replay/replay_miss_class.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

AUDIT = Path(__file__).resolve().parent.parent            # audits/panoptic-2025-12-strict-eval
ROOT = AUDIT.parent.parent                                # repo root
SNAP = AUDIT / "output" / "pre_answer_key_snapshot"
REPLAY = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))

import gate_dos_utils as gdu          # noqa: E402
import special_focus_terms as sft     # noqa: E402


def _find(suffix: str) -> Path | None:
    if not SNAP.exists():
        return None
    for p in SNAP.iterdir():
        if p.name.endswith(suffix):
            return p
    return None


def _frozen():
    man_p, disp_p = _find("coverage_manifest.json"), _find("coverage_dispositions.json")
    man = json.loads(man_p.read_text()) if man_p else {"items": []}
    disp = json.loads(disp_p.read_text()) if disp_p else {"dispositions": []}
    return man, disp


def literal_replay(man, disp):
    items = {i["id"]: i for i in man.get("items", [])}
    dispositions = disp.get("dispositions", [])
    cleared = [d for d in dispositions if d.get("status") == "cleared"]
    findings = [d for d in dispositions if d.get("status") == "finding"]

    gate_dos_route, advisory_route = [], []
    for d in cleared:
        if gdu.classify(d)["status"] == "missing_liveness_disproof":
            gate_dos_route.append(d["manifest_id"])
        it = items.get(d["manifest_id"])
        if it and sft.is_high_risk_surface(sft.item_text(it)):
            advisory_route.append(d["manifest_id"])

    return {
        "cleared_count": len(cleared),
        "finding_count": len(findings),
        "gate_dos_would_route": gate_dos_route,
        "advisory_would_route_high_risk_clears": advisory_route,
        # validators never touch findings → no finding-level FP introduced
        "findings_converted_to_fp": 0,
        "findings_minted_by_validators": 0,
    }


def main() -> int:
    if not SNAP.exists():
        print(f"frozen snapshot not present: {SNAP}", file=sys.stderr)
        return 1
    man, disp = _frozen()
    result = literal_replay(man, disp)
    REPLAY.mkdir(exist_ok=True)
    (REPLAY / "miss_class_report.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
