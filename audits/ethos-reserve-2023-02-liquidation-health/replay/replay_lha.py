#!/usr/bin/env python3
"""
replay_lha.py (Ethos Reserve 2023-02, Liquity-fork CDP) — READ-ONLY behavioral replay for the promotion freeze
regression guard.

Re-runs liquidation_health_accounting_audit against the frozen Ethos workspace and reports the routes / shapes /
helper-volume-control / wrong-domain profile. The lens only READS coverage_dispositions.json (it writes only
its own output JSON), so the workspace dispositions are untouched.

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

# Liquity-CDP liquidation/redemption/SP domain allow-set (the answer-key domain) — anything else is wrong-domain.
ALLOWED_CONTRACTS = {"TroveManager", "StabilityPool", "RedemptionHelper", "BorrowerOperations",
                     "ActivePool", "CollSurplusPool"}
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
        # confirm context_helpers provenance is carried onto a routed entrypoint that has attachments
        ctx_carried = any(disp[m].get("liquidation_health_accounting", {}).get("context_helpers")
                          for m in routed)
        return {"gate_all_needs_deep_pass": all_deep, "gate_minted_finding": minted,
                "gate_context_helpers_carried": ctx_carried,
                "gate_routed": sum(1 for m in routed
                                   if disp[m].get("assigned_agent") == "liquidation_health_accounting_review")}


def replay() -> dict:
    manifest = json.loads((AUDIT / "output" / "coverage_manifest.json").read_text())
    lens = _run_lens_against(AUDIT)
    cand = {c["manifest_id"]: c for c in lens["candidates"]}
    routed = lens.get("routed_manifest_ids", [])
    routed_fns = {(cand[m]["contract"], cand[m]["function"]) for m in routed}
    ha = lens.get("helper_attachments", {})
    # map entrypoint manifest_id -> set of attached helper function names
    attached = {cand[mid]["function"]: {h["function"] for h in hs} for mid, hs in ha.items()}
    attached_ids = {h["manifest_id"] for hs in ha.values() for h in hs}

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
        # H-01 stability-pool reward redistribution
        "h01_offset": ("StabilityPool", "offset") in routed_fns,
        "h01_update_reward_sum": ("StabilityPool", "updateRewardSum") in routed_fns,
        # M-09 redemption
        "m09_redeem_collateral": ("RedemptionHelper", "redeemCollateral") in routed_fns,
        # M-10 liquidation family (context/PARTIAL hosts)
        "m10_liquidate": ("TroveManager", "liquidate") in routed_fns,
        "m10_liquidate_troves": ("TroveManager", "liquidateTroves") in routed_fns,
        "m10_batch_liquidate_troves": ("TroveManager", "batchLiquidateTroves") in routed_fns,
        # helper volume control
        "redeem_helper_attached": "_redeemCollateralFromTrove" in attached.get("redeemCollateral", set()),
        "offset_helpers_attached": "_computeRewardsPerUnitStaked" in attached.get("offset", set()),
        "attached_not_routed": bool(attached_ids) and not (attached_ids & set(routed)),
        "routed_lt_raw": len(routed) < lens["raw_candidates"],
        **gate,
    }


if __name__ == "__main__":
    print(json.dumps(replay(), indent=2))
