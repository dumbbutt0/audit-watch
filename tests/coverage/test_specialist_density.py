"""
Task 3 — specialist swarm density enforcement. A high-density lending/vault/oracle/liquidation/NFT-collateral
target must produce the NAMED adversarial swarm outputs (access_control_init, reentrancy_callback,
permit_signature, erc4626_vault_accounting, oracle_liquidation, transformer_external_call, math_precision),
not just a single-summary DEFI-core pass (Revert Lend ran DEFI-core and still missed callback/permit/4626).
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


def _fn(name, score=4, ext=False):
    return {"id": f"function:T:{name}#x", "kind": "function", "contract": "T", "name": name,
            "in_scope": True, "attack_surface_score": score, "external_calls": ext, "tags": [], "source_span": {}}


def _manifest(ws, items, is_erc4626=False):
    (ws / "output" / "coverage_manifest.json").write_text(json.dumps({"schema_version": 1, "source": {}, "items": items}))
    (ws / "output" / "static.json").write_text(json.dumps({"is_erc4626": is_erc4626}))


def _findings(ws, names):
    for s in names:
        (ws / "output" / f"findings_{s}.json").write_text(json.dumps({"agent": s, "findings": []}))


def _run():
    old = sys.argv
    sys.argv = ["specialist_coverage_gate", "--quiet"]
    try:
        return gate.main()
    finally:
        sys.argv = old


def _dense_vault(ws):
    names = ["convertToShares", "convertToAssets", "totalAssets", "previewRedeem", "redeem",
             "liquidate", "isAccountSolvent", "onERC721Received", "getValue", "borrow"]
    _manifest(ws, [_fn(n) for n in names])


def test_high_density_requires_named_swarm(ws):
    _dense_vault(ws)
    _findings(ws, gate.DEFI_CORE_REQUIRED)   # DEFI-core present but named swarm missing
    assert _run() == 1
    rep = json.loads((ws / "output" / "specialist_coverage.json").read_text())
    assert rep["high_density"] is True
    assert "reentrancy_callback" in rep["missing"] and "permit_signature" in rep["missing"]


def test_high_density_named_swarm_present_passes(ws):
    _dense_vault(ws)
    _findings(ws, gate.DEFI_CORE_REQUIRED + gate.HIGH_DENSITY_REQUIRED)
    assert _run() == 0


def test_low_density_only_defi_core(ws):
    # one risky function among many trivial getters → density below threshold
    items = [_fn("liquidate", score=4)] + [_fn(f"get{i}", score=0) for i in range(20)]
    _manifest(ws, items)
    _findings(ws, gate.DEFI_CORE_REQUIRED)
    assert _run() == 0
    rep = json.loads((ws / "output" / "specialist_coverage.json").read_text())
    assert rep["high_density"] is False


def test_per_specialist_waiver_recall_risk(ws):
    _dense_vault(ws)
    _findings(ws, [s for s in gate.DEFI_CORE_REQUIRED + gate.HIGH_DENSITY_REQUIRED if s != "permit_signature"])
    (ws / "output" / "specialist_waiver.json").write_text(json.dumps(
        {"waivers": [{"specialist": "permit_signature", "reason": "no permit surface beyond reviewed deposit", "waived_by": "lead"}]}))
    assert _run() == 0
    assert "permit_signature" in json.loads((ws / "output" / "specialist_coverage.json").read_text())["waived_recall_risk"]
