#!/usr/bin/env python3
"""
replay_lha.py (Size Credit 2024-06) — READ-ONLY behavioral replay for the promotion freeze regression guard.

Re-runs liquidation_health_accounting_audit against the frozen Size workspace and reports the routes / shapes /
confidence / wrong-domain profile. The lens only READS coverage_dispositions.json (it writes only its own
output JSON), so the workspace dispositions are untouched.

It then performs an ISOLATED gate check in a tmp dir (copy of the frozen manifest + a fresh unassigned
dispositions for the routed ids + the lens output) to prove advisory_escalation_gate routes each high id to
needs_deep_pass (assigned_pass=deep, agent=liquidation_health_accounting_review) and NEVER mints a finding.
The real workspace is not mutated by the gate check.
"""
import importlib
import json
import os
import sys
import tempfile
from pathlib import Path

AUDIT = Path(__file__).resolve().parents[1]
SCRIPTS = AUDIT.parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_context  # noqa: E402

# liquidation/credit domain allow-set — anything outside is a wrong-domain FP.
ALLOWED_CONTRACTS = {"Compensate", "Liquidate", "LiquidateWithReplacement", "SelfLiquidate", "Repay"}
LENS_JSON = "liquidation_health_accounting_audit.json"


def _run_lens_against(root: Path) -> dict:
    audit_context.get_audit_root = lambda: root
    mod = importlib.import_module("liquidation_health_accounting_audit")
    old = sys.argv
    sys.argv = ["liquidation_health_accounting_audit", "--quiet"]
    try:
        assert mod.main() == 0
    finally:
        sys.argv = old
    return json.loads((root / "output" / LENS_JSON).read_text())


def _isolated_gate_check(manifest: dict, lens: dict) -> dict:
    """Run advisory_escalation_gate in a throwaway workspace; return whether every routed id became
    needs_deep_pass and whether any finding was minted. Does NOT touch the real workspace."""
    routed = list(lens.get("routed_manifest_ids", []))
    with tempfile.TemporaryDirectory() as td:
        ws = Path(td)
        (ws / "output").mkdir(parents=True)
        (ws / "output" / "coverage_manifest.json").write_text(json.dumps(manifest))
        (ws / "output" / "coverage_dispositions.json").write_text(json.dumps({"dispositions": [
            {"manifest_id": mid, "status": "unassigned", "evidence": [], "finding_refs": []} for mid in routed]}))
        (ws / "output" / LENS_JSON).write_text(json.dumps(lens))
        audit_context.get_audit_root = lambda: ws
        for m in ("update_coverage_dispositions", "advisory_escalation_gate"):
            if m in sys.modules:
                importlib.reload(sys.modules[m])
        gate = importlib.import_module("advisory_escalation_gate")
        importlib.reload(gate)
        prev = os.environ.get("AUDITWATCH_FULL_AUDIT")
        os.environ["AUDITWATCH_FULL_AUDIT"] = "1"
        old = sys.argv
        sys.argv = ["advisory_escalation_gate", "--quiet"]
        try:
            assert gate.main() == 0
        finally:
            sys.argv = old
            if prev is None:
                os.environ.pop("AUDITWATCH_FULL_AUDIT", None)
            else:
                os.environ["AUDITWATCH_FULL_AUDIT"] = prev
        disp = {d["manifest_id"]: d for d in
                json.loads((ws / "output" / "coverage_dispositions.json").read_text())["dispositions"]}
        all_deep = all(disp[m].get("status") == "assigned" and disp[m].get("assigned_pass") == "deep"
                       and disp[m].get("assigned_agent") == "liquidation_health_accounting_review"
                       for m in routed) if routed else False
        minted = any(disp[m].get("status") == "finding" for m in routed)
        return {"gate_all_needs_deep_pass": all_deep, "gate_minted_finding": minted,
                "gate_routed": sum(1 for m in routed
                                   if disp[m].get("assigned_agent") == "liquidation_health_accounting_review")}


def replay() -> dict:
    manifest = json.loads((AUDIT / "output" / "coverage_manifest.json").read_text())
    lens = _run_lens_against(AUDIT)
    cand = {c["manifest_id"]: c for c in lens["candidates"]}
    routed = lens.get("routed_manifest_ids", [])

    def shapes(contract, fn):
        return sorted({c["finding_shape"] for c in lens["candidates"]
                       if c["contract"] == contract and c["function"] == fn
                       and c["manifest_id"] in routed})

    routed_high_only = all(cand[m]["confidence"] == "high" and cand[m]["in_scope"] for m in routed)
    wrong_domain = sorted({c["contract"] for c in lens["candidates"]
                           if c["contract"] not in ALLOWED_CONTRACTS})
    gate = _isolated_gate_check(manifest, lens)
    return {
        "findings_minted_by_validators": 0,
        "raw_candidates": lens["raw_candidates"],
        "routed_count": len(routed),
        "routed_high_only": routed_high_only,
        "wrong_domain_contracts": wrong_domain,
        # 4 mandated seeds (shape on the routed entrypoint)
        "h03_collateral_remainder_cap": "collateral_remainder_cap" in shapes("Liquidate", "executeLiquidate"),
        "h04_liquidator_profit_bound": "liquidator_profit_bound" in shapes("Liquidate", "executeLiquidate"),
        "m09_health_factor_after_action": "health_factor_after_action" in shapes("Compensate", "executeCompensate"),
        "m11_replacement_swap_fee": "replacement_swap_fee_accounting" in
                                    shapes("LiquidateWithReplacement", "executeLiquidateWithReplacement"),
        **gate,
    }


if __name__ == "__main__":
    print(json.dumps(replay(), indent=2))
