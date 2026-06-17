"""
Tests for the beneficiary_guard_parity RESEARCH lens (P305). No LLM, no network.

Class: within one contract, some functions own-guard a beneficiary param (withApproval(owner)/require(msg.sender==
owner)) while sibling functions take a beneficiary param UNGUARDED -> act-for-others griefing. From the P304
centrifuge M-04 miss.

Covers: unguarded beneficiary sibling (given a guarded sibling) fires; the guarded fn itself silent; admin-guarded
silent; view silent; no-guarded-sibling contract silent; interface (*Like) suppressed; research-only flags;
centrifuge anchor recovery (LiquidityPool.deposit/mint fire).
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_context  # noqa: E402
bgp = importlib.import_module("beneficiary_guard_parity_taxonomy")
audit = importlib.import_module("beneficiary_guard_parity_audit")


# 1. unguarded beneficiary sibling (contract HAS an owner-guarded sibling) -> fires
def test_unguarded_sibling_fires():
    out = bgp.classify_function("deposit", "function deposit(uint256 assets, address receiver) public returns (uint256)",
                                "{ _mint(receiver, assets); }", "public", contract_has_owner_guard=True)
    assert out and out[0]["finding_shape"] == "beneficiary_guard_parity" and out[0]["beneficiary_role"] == "receiver"


# 2. the owner-guarded function itself -> not the weak sibling (silent)
def test_guarded_fn_silent():
    out = bgp.classify_function("withdraw", "function withdraw(uint256 a, address receiver, address owner) public withApproval(owner) returns (uint256)",
                                "{ _burn(owner, a); }", "public", contract_has_owner_guard=True)
    assert out == []


# 3. admin-guarded (auth) beneficiary fn -> silent
def test_admin_guarded_silent():
    out = bgp.classify_function("mintTo", "function mintTo(address account, uint256 v) external auth",
                                "{ balanceOf[account] += v; }", "external", contract_has_owner_guard=True)
    assert out == []


# 4. view fn -> silent
def test_view_silent():
    out = bgp.classify_function("balanceOfOwner", "function balanceOfOwner(address owner) public view returns (uint256)",
                                "{ return balanceOf[owner]; }", "public", contract_has_owner_guard=True)
    assert out == []


# 5. no owner-guarded sibling in the contract -> no asymmetry -> silent
def test_no_guarded_sibling_silent():
    out = bgp.classify_function("deposit", "function deposit(uint256 assets, address receiver) public returns (uint256)",
                                "{ _mint(receiver, assets); }", "public", contract_has_owner_guard=False)
    assert out == []


# 6. helpers: beneficiary_param + owner_guarded detection
def test_helpers():
    assert bgp.beneficiary_param("function f(uint256 a, address receiver)") == "receiver"
    assert bgp.beneficiary_param("function f(address to, uint256 a)") is None  # 'to' not a beneficiary role
    assert bgp.owner_guarded("function f(address owner) public withApproval(owner)", "{}") is True
    assert bgp.owner_guarded("function f(address owner) public", "{ require(msg.sender == owner); }") is True
    assert bgp.owner_guarded("function f(address owner) public", "{ doThing(); }") is False


# 7. research-only flags via the runner (+ *Like interface suppression)
def test_research_only_flags(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    (tmp_path / "output" / "coverage_manifest.json").write_text(json.dumps({"schema_version": 1, "items": [
        {"id": "function:C:f#x", "kind": "function", "contract": "C", "name": "f", "file": "none.sol",
         "signature": "function f(address receiver) external", "source_span": {"start_line": 1, "end_line": 1}, "in_scope": True}]}))
    old = sys.argv
    sys.argv = ["beneficiary_guard_parity_audit", "--quiet", "--no-source"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((tmp_path / "output" / "beneficiary_guard_parity_audit.json").read_text())
    assert r["is_gate"] is False and r["research_only"] is False and r["promotion"] == "advisory_only" and r["routes_in_production"] is False
    assert r["routed_manifest_ids"] == []


# 8. read-only centrifuge anchor recovery: LiquidityPool.deposit/mint fire, interfaces suppressed, controlled volume
def test_centrifuge_anchor_recovery(monkeypatch):
    cf = ROOT / "audits" / "centrifuge-2023-09-holdout"
    if not (cf / "output" / "coverage_manifest.json").exists():
        pytest.skip("centrifuge manifest not present")
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: cf)
    audit._FILE_CACHE.clear()
    old = sys.argv
    sys.argv = ["beneficiary_guard_parity_audit", "--manifest", str(cf / "output" / "coverage_manifest.json"), "--quiet"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((cf / "output" / "beneficiary_guard_parity_audit.json").read_text())
    byfn = {(c["contract"], c["function"]) for c in r["candidates"]}
    assert ("LiquidityPool", "deposit") in byfn and ("LiquidityPool", "mint") in byfn   # the anchor (M-04)
    assert not any(c["contract"].endswith("Like") for c in r["candidates"])             # interfaces suppressed
    assert r["raw_candidates"] <= 8, f"volume not controlled: {r['raw_candidates']}"
    assert r["routes_in_production"] is False and r["routed_manifest_ids"] == []
