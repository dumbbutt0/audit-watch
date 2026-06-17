"""
Tests for the nonstandard_permit RESEARCH lens (P303). No LLM, no network.

Class: hard-coded EIP-2612 permit on a configurable/external asset with no resilience -> reverts for DAI/non-2612
assets -> permit/deposit DoS. Generalized from the P302 pooltogether M-08 miss.

Covers: anchor-style depositWithPermit -> high; self/own-share-token permit -> suppressed; try/catch resilience ->
suppressed; Permit2 fallback -> suppressed; router/param-token -> suppressed; permit-primitive library ->
suppressed; no permit consumption -> no candidate; research-only flags + routed_manifest_ids == []; and a read-only
pooltogether anchor recovery (depositWithPermit high, controlled volume).
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_context  # noqa: E402
nsp = importlib.import_module("nonstandard_permit_taxonomy")
audit = importlib.import_module("nonstandard_permit_audit")


def _c(name, body, sig="", contract="Vault", kind="function"):
    return nsp.classify(name, sig, "f.sol", contract, snippet=body, kind=kind)


# anchor-style: hard-coded EIP-2612 permit on the configurable external _asset, no try/catch, no Permit2 fallback
_ANCHOR = """function depositWithPermit(uint256 _assets, address _owner, uint256 _deadline, uint8 _v, bytes32 _r, bytes32 _s) external returns (uint256) {
  if (_owner != msg.sender) { revert PermitCallerNotOwner(msg.sender, _owner); }
  if (_asset.allowance(_owner, address(this)) != _assets) {
    IERC20Permit(address(_asset)).permit(_owner, address(this), _assets, _deadline, _v, _r, _s);
  }
  uint256 _shares = previewDeposit(_assets);
  _depositAndMint(_owner, _owner, _assets, _shares);
}"""


# 1. anchor-style hard-coded 2612 permit on external asset -> high
def test_anchor_high():
    out = _c("depositWithPermit", _ANCHOR, sig="uint256 _assets, address _owner, uint256 _deadline, uint8 _v, bytes32 _r, bytes32 _s")
    assert out and out[0]["confidence"] == "high"
    assert out[0]["finding_shape"] == "nonstandard_permit_hardcoded"
    assert out[0]["suppression_status"] == "none"


# 2. permit on the contract's OWN 2612 share token -> suppressed (2612 by construction)
def test_self_token_suppressed():
    body = """function permitDeposit(uint256 v, uint256 deadline, uint8 _v, bytes32 r, bytes32 s) external {
      IERC20Permit(address(this)).permit(msg.sender, address(this), v, deadline, _v, r, s);
    }"""
    assert _c("permitDeposit", body) == []


# 3. try/catch resilience -> suppressed
def test_trycatch_suppressed():
    body = _ANCHOR.replace(
        "IERC20Permit(address(_asset)).permit(_owner, address(this), _assets, _deadline, _v, _r, _s);",
        "try IERC20Permit(address(_asset)).permit(_owner, address(this), _assets, _deadline, _v, _r, _s) {} catch {}")
    assert _c("depositWithPermit", body) == []


# 4. Permit2 / DAI-allowed fallback present -> resilient -> suppressed
def test_permit2_fallback_suppressed():
    body = """function depositWithPermit(uint256 _assets, uint256 _deadline, uint8 _v, bytes32 _r, bytes32 _s) external {
      if (supportsPermit2) { permit2.permitTransferFrom(p, d, msg.sender, sig); }
      else { IERC20Permit(address(_asset)).permit(msg.sender, address(this), _assets, _deadline, _v, _r, _s); }
    }"""
    assert _c("depositWithPermit", body) == []


# 5. router / caller-supplied token param -> suppressed
def test_router_param_suppressed():
    body = """function pullWithPermit(address token, uint256 amt, uint256 deadline, uint8 v, bytes32 r, bytes32 s) external {
      IERC20Permit(token).permit(msg.sender, address(this), amt, deadline, v, r, s);
    }"""
    assert _c("pullWithPermit", body, sig="address token, uint256 amt, uint256 deadline, uint8 v, bytes32 r, bytes32 s", contract="SwapRouter") == []
    # also suppressed purely by the token-param signal even without the router name
    assert _c("pull", body, sig="address token, uint256 amt", contract="Helper") == []


# 6. permit primitive library -> suppressed
def test_permit_library_suppressed():
    body = "function permit(address owner, address spender, uint256 value, uint256 deadline, uint8 v, bytes32 r, bytes32 s) public { _approve(owner, spender, value); }"
    assert _c("permit", body, contract="ERC20Permit", kind="library") == []


# 7. no permit consumption -> no candidate
def test_no_permit_no_candidate():
    body = "function deposit(uint256 assets) external { _asset.safeTransferFrom(msg.sender, address(this), assets); }"
    assert _c("deposit", body) == []


# 8. Permit2-only flow (no 2612 fingerprint, no IERC20Permit) -> no candidate (not the hard-coded-2612 class)
def test_permit2_only_no_candidate():
    body = "function pull(uint256 amt) external { permit2.permitTransferFrom(permit, details, msg.sender, sig); uint256 a = asset(); }"
    assert _c("pull", body) == []


# 9. research-only flags via the runner
def test_research_only_flags(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    (tmp_path / "output" / "coverage_manifest.json").write_text(json.dumps({"schema_version": 1, "items": [
        {"id": "function:C:f#x", "kind": "function", "contract": "C", "name": "f", "file": "none.sol",
         "signature": "", "source_span": {"start_line": 1, "end_line": 1}, "in_scope": True}]}))
    old = sys.argv
    sys.argv = ["nonstandard_permit_audit", "--quiet"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((tmp_path / "output" / "nonstandard_permit_audit.json").read_text())
    assert r["is_gate"] is False and r["research_only"] is False and r["promotion"] == "advisory_only" and r["routes_in_production"] is False
    assert r["routed_manifest_ids"] == []


# 10. read-only pooltogether anchor recovery: depositWithPermit high, controlled volume, no wrong-domain spread
def test_pooltogether_anchor_recovery(monkeypatch):
    pt = ROOT / "audits" / "pooltogether-2024-03-holdout"
    if not (pt / "output" / "coverage_manifest.json").exists():
        pytest.skip("pooltogether manifest not present")
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: pt)
    audit._FILE_CACHE.clear()
    old = sys.argv
    sys.argv = ["nonstandard_permit_audit", "--manifest", str(pt / "output" / "coverage_manifest.json"), "--quiet"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((pt / "output" / "nonstandard_permit_audit.json").read_text())
    byfn = {(c["contract"], c["function"]): c["confidence"] for c in r["candidates"]}
    assert byfn.get(("PrizeVault", "depositWithPermit")) == "high"   # the anchor (M-08)
    assert r["raw_candidates"] <= 4, f"volume not controlled: {r['raw_candidates']}"
    assert r["routes_in_production"] is False and r["routed_manifest_ids"] == []
