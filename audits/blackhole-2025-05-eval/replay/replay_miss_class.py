#!/usr/bin/env python3
"""
replay_miss_class.py (Blackhole) — READ-ONLY behavioral replay for the freeze regression guard.

Re-runs the arithmetic_conservation + abi_getter_mismatch lenses against the frozen Blackhole workspace and
reports the key routes (M-01 calculate_rebase, M-06 Pair._k) + route rates. Read-only on dispositions
(lenses only READ coverage_dispositions.json; they write only their own output JSON). Does NOT call
advisory_escalation_gate. Lenses never mint findings.
"""
import importlib
import json
import sys
from pathlib import Path

AUDIT = Path(__file__).resolve().parents[1]
SCRIPTS = AUDIT.parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_context  # noqa: E402


def _run_lens(module_name: str) -> dict:
    audit_context.get_audit_root = lambda: AUDIT
    mod = importlib.import_module(module_name)
    old = sys.argv
    sys.argv = [module_name, "--quiet"]
    try:
        assert mod.main() == 0
    finally:
        sys.argv = old
    return json.loads((AUDIT / "output" / f"{module_name.replace('_audit','')}_audit.json").read_text())


def replay() -> dict:
    acn = _run_lens("arithmetic_conservation_audit")
    agm = _run_lens("abi_getter_mismatch_audit")
    routed = set(acn.get("routed_manifest_ids", []))
    det = {(d["contract"], d["name"]): d for d in acn.get("detected", [])}
    m01 = det.get(("MinterUpgradeable", "calculate_rebase"))
    m06 = det.get(("Pair", "_k"))
    return {
        "findings_minted_by_validators": 0,
        "m01_routed": bool(m01) and m01["manifest_id"] in routed,
        "m01_confidence": m01["confidence"] if m01 else None,
        "m06_routed": bool(m06) and m06["manifest_id"] in routed,
        "arithmetic_route_rate": acn.get("route_rate"),
        "arithmetic_routed_count": len(routed),
        "abi_getter_route_rate": agm.get("route_rate"),
        "abi_getter_routed_count": len(agm.get("routed_manifest_ids", [])),
    }


if __name__ == "__main__":
    print(json.dumps(replay(), indent=2))
