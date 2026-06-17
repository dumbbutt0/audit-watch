#!/usr/bin/env python3
"""
replay_miss_class.py (Hybra) — READ-ONLY behavioral replay for the freeze regression guard.

Re-runs the two post-answer-key lenses against the frozen Hybra workspace and reports their routes. Calls
each lens's audit.main() (read-only on dispositions — it only READS coverage_dispositions.json; it writes
only its own output/<lens>_audit.json). Does NOT call advisory_escalation_gate (that would write
dispositions). Lenses never mint findings, so findings_minted_by_validators is 0 by construction.
"""
import importlib
import json
import sys
from pathlib import Path

AUDIT = Path(__file__).resolve().parents[1]
SCRIPTS = AUDIT.parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_context  # noqa: E402

M07_ID = "function:GrowthHYBR:claimRewards#7c235721"


def _run_lens(module_name: str) -> dict:
    audit_context.get_audit_root = lambda: AUDIT          # point the lens at this eval (read-only on disp)
    mod = importlib.import_module(module_name)
    old = sys.argv
    sys.argv = [module_name, "--quiet"]
    try:
        assert mod.main() == 0
    finally:
        sys.argv = old
    return json.loads((AUDIT / "output" / f"{module_name.replace('_audit','')}_audit.json").read_text())


def replay() -> dict:
    agm = _run_lens("abi_getter_mismatch_audit")
    acn = _run_lens("arithmetic_conservation_audit")
    p3 = json.loads((AUDIT / "output" / "eval_ready" / "p1p2_fresh" / "p3_loop_reduction.json").read_text())
    return {
        "findings_minted_by_validators": 0,
        "m07_routed": M07_ID in agm.get("routed_manifest_ids", []),
        "abi_getter_route_rate": agm.get("route_rate"),
        "arithmetic_route_rate": acn.get("route_rate"),
        "arithmetic_routed_count": len(acn.get("routed_manifest_ids", [])),
        "reward_loops_baseline": p3.get("baseline_incomplete_reward_routes"),
        "reward_loops_after_p3": p3.get("p3_incomplete_reward_routes"),
        "p1_still_rejects_prose": p3.get("p1_still_rejects_prose"),
    }


if __name__ == "__main__":
    print(json.dumps(replay(), indent=2))
