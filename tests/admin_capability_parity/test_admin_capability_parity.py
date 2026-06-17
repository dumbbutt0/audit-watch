"""
Tests for the admin_capability_parity RESEARCH lens (P305). No LLM, no network.

Class: an admin/role contract exposes one half of a capability pair (pause/unpause, add/remove role, grant/revoke,
schedule/cancel, ...) but not the inverse. From the P304 centrifuge M-06 miss.

Covers: pause without unpause (admin) fires; both halves silent; non-admin contract silent; append-only registry
(addPool, non-role suffix) silent; role grant without revoke (addPauser w/o removePauser) fires; camelCase boundary
(no 'additional' FP); research-only flags; centrifuge anchor recovery (PauseAdmin fires).
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_context  # noqa: E402
acp = importlib.import_module("admin_capability_parity_taxonomy")
audit = importlib.import_module("admin_capability_parity_audit")

_ADMIN_BLOB = "modifier auth { require(wards[msg.sender] == 1); } root.pause();"


# 1. admin contract: pause without unpause -> fires
def test_pause_without_unpause_fires():
    out = acp.classify_contract("PauseAdmin", ["pause", "addPauser", "removePauser"], _ADMIN_BLOB)
    miss = {c["missing_inverse"] for c in out}
    assert "unpause" in miss


# 2. both halves present -> silent
def test_symmetric_silent():
    out = acp.classify_contract("DelayedAdmin", ["pause", "unpause", "scheduleRely", "cancelRely"], _ADMIN_BLOB)
    assert out == []


# 3. non-admin contract -> silent
def test_non_admin_silent():
    out = acp.classify_contract("SwapPool", ["pause", "swap", "addLiquidity"], "function swap() external {}")
    assert out == []


# 4. append-only registry (non-role suffix) -> silent (add/remove gated to role suffixes)
def test_registry_add_silent():
    out = acp.classify_contract("PoolManager", ["addPool", "addTranche", "addCurrency"], _ADMIN_BLOB)
    assert out == []


# 5. role grant without revoke -> fires (addPauser without removePauser)
def test_role_add_without_remove_fires():
    out = acp.classify_contract("Roles", ["addMinter"], _ADMIN_BLOB)
    assert any(c["missing_inverse"] == "removeMinter" for c in out)


# 6. camelCase boundary: 'additional' must not match the 'add' prefix
def test_camelcase_boundary():
    assert acp._matches_prefix("additional", "add") is None
    assert acp._matches_prefix("addMinter", "add") == "Minter"
    assert acp._matches_prefix("pause", "pause") == ""


# 7. research-only flags via the runner
def test_research_only_flags(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    (tmp_path / "output" / "coverage_manifest.json").write_text(json.dumps({"schema_version": 1, "items": [
        {"id": "function:PauseAdmin:pause#x", "kind": "function", "contract": "PauseAdmin", "name": "pause",
         "file": "none.sol", "signature": "function pause() public auth", "source_span": {"start_line": 1, "end_line": 1}, "in_scope": True}]}))
    old = sys.argv
    sys.argv = ["admin_capability_parity_audit", "--quiet", "--no-source"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((tmp_path / "output" / "admin_capability_parity_audit.json").read_text())
    assert r["is_gate"] is False and r["research_only"] is False and r["promotion"] == "advisory_only" and r["routes_in_production"] is False
    assert r["routed_manifest_ids"] == []


# 8. read-only centrifuge anchor recovery: PauseAdmin fires, controlled volume
def test_centrifuge_anchor_recovery(monkeypatch):
    cf = ROOT / "audits" / "centrifuge-2023-09-holdout"
    if not (cf / "output" / "coverage_manifest.json").exists():
        pytest.skip("centrifuge manifest not present")
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: cf)
    audit._FILE_CACHE.clear()
    old = sys.argv
    sys.argv = ["admin_capability_parity_audit", "--manifest", str(cf / "output" / "coverage_manifest.json"), "--quiet"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((cf / "output" / "admin_capability_parity_audit.json").read_text())
    pairs = {(c["contract"], c["present_capability"], c["missing_inverse"]) for c in r["candidates"]}
    assert ("PauseAdmin", "pause", "unpause") in pairs   # the anchor (M-06 subsystem)
    assert r["raw_candidates"] <= 4, f"volume not controlled: {r['raw_candidates']}"
    assert r["routes_in_production"] is False and r["routed_manifest_ids"] == []
