"""
Tests for the permit_asset_binding RESEARCH prototype (Shape A: Permit2 asset-binding missing). No LLM, no network.

Covers: the anchor-style vault permit-without-binding -> high; the same WITH an explicit permitted.token == asset
check -> suppressed; a multi-asset router (token param / router name + selfPermit) -> suppressed; a permit
primitive library -> suppressed; an ERC4626 asset() vault permit-without-binding -> high; a no-permit function ->
no candidate; research-only flags + routed_manifest_ids == []; and a read-only Revert Lend anchor recovery
(V3Vault permit functions high, controlled volume, constructor NOT flagged).
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_context  # noqa: E402
pab = importlib.import_module("permit_asset_binding_taxonomy")
audit = importlib.import_module("permit_asset_binding_audit")


def _c(name, body, sig="", contract="Vault", kind="function"):
    return pab.classify(name, sig, "f.sol", contract, snippet=body, kind=kind)


# anchor-style: vault consumes permit2.permitTransferFrom, references IERC20(asset), no token==asset check
_ANCHOR = """function _deposit(address receiver, uint256 assets, bytes memory permitData) internal {
  if (permitData.length > 0) {
    (ISignatureTransfer.PermitTransferFrom memory permit, bytes memory signature) = abi.decode(permitData, (ISignatureTransfer.PermitTransferFrom, bytes));
    permit2.permitTransferFrom(permit, ISignatureTransfer.SignatureTransferDetails(address(this), assets), msg.sender, signature);
  } else {
    SafeERC20.safeTransferFrom(IERC20(asset), msg.sender, address(this), assets);
  }
}"""


# 1. anchor-style permit-without-binding -> high
def test_anchor_high():
    out = _c("_deposit", _ANCHOR)
    assert out and out[0]["confidence"] == "high"
    assert out[0]["finding_shape"] == "permit_asset_binding_missing"
    assert out[0]["suppression_status"] == "none"


# 2. explicit validation present (permitted.token == asset) -> suppressed (no candidate)
def test_explicit_binding_suppressed():
    body = _ANCHOR.replace(
        "permit2.permitTransferFrom(permit,",
        "require(permit.permitted.token == asset, \"InvalidToken\"); permit2.permitTransferFrom(permit,")
    assert _c("_deposit", body) == []


# 3. multi-asset router: arbitrary token param + router contract + selfPermit -> suppressed
def test_router_suppressed():
    body = """function swap(address tokenIn, uint256 amountIn, bytes calldata permitData) external {
      permit2.permitTransferFrom(permit, details, msg.sender, sig);
      IERC20(tokenIn).approve(pool, amountIn);
    }"""
    assert _c("swap", body, sig="address tokenIn, uint256 amountIn", contract="SwapRouter") == []
    # also suppressed purely by the token-param signal even without the router name
    assert _c("pull", body, sig="address tokenIn, uint256 amountIn", contract="Helper") == []


# 4. permit primitive library -> suppressed
def test_permit_library_suppressed():
    body = "function permitTransferFrom(PermitTransferFrom memory permit, SignatureTransferDetails calldata d, address owner, bytes calldata sig) external { _permitTransferFrom(permit, d, owner, sig); }"
    assert _c("permitTransferFrom", body, contract="SignatureTransfer", kind="library") == []
    assert _c("selfPermit", "function selfPermit(address token, uint256 v, uint256 d, uint8 vv, bytes32 r, bytes32 s) public { IERC20Permit(token).permit(msg.sender, address(this), v, d, vv, r, s); }", contract="SelfPermit") == []


# 5. ERC4626 asset() vault permit-without-binding -> high
def test_erc4626_asset_getter_high():
    body = """function depositWithPermit(uint256 assets, bytes calldata permitData) external {
      (ISignatureTransfer.PermitTransferFrom memory permit, bytes memory sig) = abi.decode(permitData, (ISignatureTransfer.PermitTransferFrom, bytes));
      permit2.permitTransferFrom(permit, ISignatureTransfer.SignatureTransferDetails(address(this), assets), msg.sender, sig);
      _mintShares(assets);
      uint256 a = asset();
    }"""
    out = _c("depositWithPermit", body, contract="ERC4626Vault")
    assert out and out[0]["confidence"] == "high"


# 6. no permit consumption -> no candidate
def test_no_permit_no_candidate():
    body = "function deposit(uint256 assets) external { SafeERC20.safeTransferFrom(IERC20(asset), msg.sender, address(this), assets); }"
    assert _c("deposit", body) == []


# 7. permit consumed but NO bound asset (asset-agnostic, token from param) -> no candidate
def test_no_bound_asset_no_candidate():
    body = "function pull(address token, uint256 amt) external { permit2.permitTransferFrom(permit, ISignatureTransfer.SignatureTransferDetails(address(this), amt), msg.sender, sig); }"
    assert _c("pull", body, sig="address token, uint256 amt") == []


# 8. ERC2612 .permit() consumed into a single-asset vault, no binding -> candidate
def test_erc2612_permit_high():
    body = """function depositWithPermit(uint256 assets, uint8 v, bytes32 r, bytes32 s, uint256 deadline) external {
      IERC20Permit(address(asset)).permit(msg.sender, address(this), assets, deadline, v, r, s);
      IERC20(asset).transferFrom(msg.sender, address(this), assets);
    }"""
    out = _c("depositWithPermit", body, contract="LendingPool")
    assert out and out[0]["confidence"] in ("high", "medium")


# 9. has_permit_consumption gate: a type ref / assignment is NOT consumption
def test_consumption_gate():
    assert pab.has_permit_consumption("permit2 = IPermit2(_p); asset = _asset;") is False
    assert pab.has_permit_consumption("permit2.permitTransferFrom(permit, d, o, s);") is True


# 10. research-only flags via the runner
def test_research_only_flags(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    (tmp_path / "output" / "coverage_manifest.json").write_text(json.dumps({"schema_version": 1, "items": [
        {"id": "function:C:f#x", "kind": "function", "contract": "C", "name": "f", "file": "none.sol",
         "signature": "", "source_span": {"start_line": 1, "end_line": 1}, "in_scope": True}]}))
    old = sys.argv
    sys.argv = ["permit_asset_binding_audit", "--quiet"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((tmp_path / "output" / "permit_asset_binding_audit.json").read_text())
    assert r["is_gate"] is False and r["research_only"] is True and r["routes_in_production"] is False
    assert r["routed_manifest_ids"] == []


# 11. read-only Revert Lend anchor recovery: V3Vault permit fns high, constructor not flagged, volume controlled
def test_revert_anchor_recovery(monkeypatch):
    rv = ROOT / "audits" / "revert-lend-2024-03-strict-eval"
    if not (rv / "output" / "coverage_manifest.json").exists():
        pytest.skip("Revert Lend manifest not present")
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: rv)
    audit._FILE_CACHE.clear()
    old = sys.argv
    sys.argv = ["permit_asset_binding_audit", "--manifest", str(rv / "output" / "coverage_manifest.json"), "--quiet"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((rv / "output" / "permit_asset_binding_audit.json").read_text())
    byfn = {(c["contract"], c["function"]): c["confidence"] for c in r["candidates"]}
    assert byfn.get(("V3Vault", "_deposit")) == "high"            # the anchor
    assert ("V3Vault", "constructor") not in byfn                  # consumption gate excludes the ctor
    assert all(c["contract"] == "V3Vault" for c in r["candidates"])  # no wrong-domain spread
    assert r["raw_candidates"] <= 8, f"volume not controlled: {r['raw_candidates']}"
    assert r["routes_in_production"] is False and r["routed_manifest_ids"] == []
