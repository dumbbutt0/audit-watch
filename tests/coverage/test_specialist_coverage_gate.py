"""
Task 2 — mandatory specialist coverage by target profile.

A vault/liquidation/oracle target must not freeze if the reentrancy / access-control / oracle / etc.
specialists never ran (the Panoptic miss: both Highs were reentrancy + access-control). The gate detects
the profile from manifest function names + static flags and blocks (strict full-audit) on a missing
required specialist unless a waiver is recorded.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import audit_context  # noqa: E402
gate = importlib.import_module("specialist_coverage_gate")


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    monkeypatch.setenv("AUDITWATCH_FULL_AUDIT", "1")
    return tmp_path


def _fn(name):
    return {"id": f"function:T:{name}#x", "kind": "function", "contract": "T", "name": name,
            "in_scope": True, "attack_surface_score": 3, "tags": [], "source_span": {}}


def _vault_liq_manifest(ws):
    names = ["convertToShares", "convertToAssets", "totalAssets", "previewRedeem", "redeem",
             "liquidate", "isAccountSolvent", "getLiquidationBonus", "settleLiquidation", "twapEMA"]
    (ws / "output" / "coverage_manifest.json").write_text(json.dumps(
        {"schema_version": 1, "source": {}, "items": [_fn(n) for n in names]}))
    (ws / "output" / "static.json").write_text(json.dumps({"is_erc4626": False}))


def _findings(ws, specialists):
    for s in specialists:
        (ws / "output" / f"findings_{s}.json").write_text(json.dumps({"agent": s, "findings": []}))


def _run():
    old = sys.argv
    sys.argv = ["specialist_coverage_gate", "--quiet"]
    try:
        return gate.main()
    finally:
        sys.argv = old


def test_profile_detected_and_missing_specialist_blocks(ws):
    _vault_liq_manifest(ws)
    _findings(ws, ["logic", "arithmetic", "oracle", "economic_attack", "erc4626", "access_control"])  # reentrancy MISSING
    assert _run() == 1
    rep = json.loads((ws / "output" / "specialist_coverage.json").read_text())
    assert "erc4626_shares" in rep["profiles"] and "lending_liquidation_solvency" in rep["profiles"]
    assert "reentrancy" in rep["missing"]


def test_all_required_present_passes(ws):
    _vault_liq_manifest(ws)   # dense → also requires the high-density named swarm
    _findings(ws, gate.DEFI_CORE_REQUIRED + gate.HIGH_DENSITY_REQUIRED)
    assert _run() == 0
    rep = json.loads((ws / "output" / "specialist_coverage.json").read_text())
    assert rep["missing"] == [] and rep["high_density"] is True


def test_waiver_unblocks(ws):
    _vault_liq_manifest(ws)
    _findings(ws, [s for s in gate.DEFI_CORE_REQUIRED + gate.HIGH_DENSITY_REQUIRED if s != "reentrancy"])
    (ws / "output" / "specialist_waiver.json").write_text(json.dumps(
        {"waivers": [{"specialist": "reentrancy", "reason": "budget; deferred to follow-up", "waived_by": "lead"}]}))
    assert _run() == 0
    assert json.loads((ws / "output" / "specialist_coverage.json").read_text())["waived_recall_risk"]


def test_non_defi_target_has_no_requirement(ws):
    (ws / "output" / "coverage_manifest.json").write_text(json.dumps(
        {"schema_version": 1, "source": {}, "items": [_fn("ping"), _fn("setGreeting"), _fn("name")]}))
    (ws / "output" / "static.json").write_text(json.dumps({"is_erc4626": False}))
    assert _run() == 0
    rep = json.loads((ws / "output" / "specialist_coverage.json").read_text())
    assert rep["profiles"] == [] and rep["required"] == []


def test_advisory_mode_warns_only(ws, monkeypatch):
    monkeypatch.delenv("AUDITWATCH_FULL_AUDIT", raising=False)
    _vault_liq_manifest(ws)
    _findings(ws, [])      # nothing ran
    assert _run() == 0     # advisory → warn, no block
    assert json.loads((ws / "output" / "specialist_coverage.json").read_text())["strict"] is False
