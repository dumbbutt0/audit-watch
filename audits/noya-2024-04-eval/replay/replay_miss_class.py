#!/usr/bin/env python3
"""
replay_miss_class.py (NOYA) — READ-ONLY behavioral replay for the freeze regression guard.

Re-runs (in order) arithmetic_conservation -> connector_position_accounting -> abi_getter_mismatch against
the frozen NOYA workspace and reports the connector/TVL routes + the H-08 special_focus signal. Read-only on
dispositions (lenses only READ coverage_dispositions.json; they write only their own output JSON). Does NOT
call advisory_escalation_gate. Lenses never mint findings. arithmetic_conservation must run first so
connector_position_accounting can de-dup against it (Aerodrome).
"""
import importlib
import json
import sys
from pathlib import Path

AUDIT = Path(__file__).resolve().parents[1]
SCRIPTS = AUDIT.parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_context  # noqa: E402
import special_focus_terms as sft  # noqa: E402


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


def _h08_special_focus() -> bool:
    man = json.loads((AUDIT / "output" / "coverage_manifest.json").read_text()).get("items", [])
    hits = [it for it in man if it.get("name") == "sendTokensToTrustedAddress"]
    return any(sft.is_special_focus(it) for it in hits)


def replay() -> dict:
    acn = _run_lens("arithmetic_conservation_audit")          # first: connector lens de-dups against it
    cpa = _run_lens("connector_position_accounting_audit")
    agm = _run_lens("abi_getter_mismatch_audit")

    cpa_routed = set(cpa.get("routed_manifest_ids", []))
    cpa_ctx = set(cpa.get("context_only", []))
    cpa_det = {(d["contract"], d["name"]): d for d in cpa.get("detected", [])}
    acn_routed = set(acn.get("routed_manifest_ids", []))
    acn_det = {(d["contract"], d["name"]): d for d in acn.get("detected", [])}

    def routed_shape(contract, name):
        d = cpa_det.get((contract, name))
        return (d["shape"], d["confidence"]) if d and d["manifest_id"] in cpa_routed else None

    aero = cpa_det.get(("AerodromeConnector", "_getPositionTVL"))
    aero_acn = acn_det.get(("AerodromeConnector", "_getPositionTVL"))
    return {
        "findings_minted_by_validators": 0,
        "h11_snx": routed_shape("SNXV3Connector", "_getPositionTVL"),
        "h19_morpho": routed_shape("MorphoBlueConnector", "_getPositionTVL"),
        "h13_balancer": routed_shape("BalancerConnector", "_getPositionTVL"),
        "h12_registry": routed_shape("PositionRegistry", "updateHoldingPosition"),
        "aerodrome_deduped_to_context": bool(aero) and aero["manifest_id"] in cpa_ctx,
        "aerodrome_owned_by_arithmetic": bool(aero_acn) and aero_acn["manifest_id"] in acn_routed,
        "cpa_route_rate": cpa.get("route_rate"),
        "cpa_dedup_count": cpa.get("dedup_arithmetic_conservation"),
        "abi_getter_route_rate": agm.get("route_rate"),
        "h08_special_focus": _h08_special_focus(),
    }


if __name__ == "__main__":
    print(json.dumps(replay(), indent=2))
