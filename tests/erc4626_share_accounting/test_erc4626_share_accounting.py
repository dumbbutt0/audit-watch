"""
Tests for the erc4626_share_accounting RESEARCH family (NARROW). No LLM/network. Synthetic ADVANCE/REJECT + negative
controls + a mechanism-based replay over the real PoolTogether PrizeVault._maxYieldVaultWithdraw anchor (M-02:
convertToAssets(maxRedeem()) where EIP-4626 mandates previewRedeem).
"""
import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

e46 = importlib.import_module("erc4626_share_accounting_taxonomy")
audit = importlib.import_module("erc4626_share_accounting_audit")


def _c(name, body, is4626=True, contract="V"):
    return e46.classify(contract, name, "", body, is4626=is4626)


# 1. 4626 vault: maxWithdraw uses convertToAssets(maxRedeem) -> ADVANCE high
def test_1_convert_in_max_advances():
    body = "function maxWithdraw(address o) public view returns (uint256) { return yieldVault.convertToAssets(yieldVault.maxRedeem(address(this))); }"
    out = _c("maxWithdraw", body)
    assert out and out[0]["confidence"] == "high", out
    assert out[0]["finding_shape"] == "erc4626_convert_in_max_misuse"


# 2. 4626 vault: maxWithdraw uses previewRedeem (correct) -> REJECT
def test_2_preview_correct_rejected():
    body = "function maxWithdraw(address o) public view returns (uint256) { return yieldVault.previewRedeem(yieldVault.maxRedeem(address(this))); }"
    assert _c("maxWithdraw", body) == []


# 3. non-4626 contract -> REJECT
def test_3_non_4626_rejected():
    body = "function maxWithdraw(address o) public view returns (uint256) { return token.convertToAssets(x); }"
    assert _c("maxWithdraw", body, is4626=False) == []


# 4. 4626 vault but a non-max/preview function using convertTo* -> REJECT (fn-kind fails)
def test_4_non_max_fn_rejected():
    body = "function deposit(uint256 a) external { uint256 s = convertToShares(a); _mint(msg.sender, s); }"
    assert _c("deposit", body) == []


# 5. (P242 precision fix) 4626 vault: previewWithdraw using its OWN convertToAssets (no external-max wrapper) ->
#    REJECT. Bare preview*/max* using own convertTo* is the common compliant pattern (was broad noise across every
#    vault: sentiment 8, concrete 5) -> now suppressed; only the external-max wrapper (M-02 shape) fires.
def test_5_own_convert_no_external_max_rejected():
    body = "function previewWithdraw(uint256 a) public view returns (uint256) { return convertToAssets(a); }"
    assert _c("previewWithdraw", body) == []


# 6. documented behavior -> REJECT
def test_6_documented_rejected():
    body = "// shares represent how many assets an account has deposited\nfunction maxWithdraw(address o) public view returns (uint256) { return convertToAssets(maxRedeem(o)); }"
    assert _c("maxWithdraw", body) == []


# is_4626 detector
def test_is4626_detection():
    assert e46.is_4626_contract("contract V is IERC4626 { }")
    assert e46.is_4626_contract("function convertToShares() {} function convertToAssets() {}")
    assert not e46.is_4626_contract("function deposit() {} function transfer() {}")


# ---- mechanism-based replay: real PrizeVault._maxYieldVaultWithdraw anchor (M-02) ----
def test_pooltogether_anchor_recovered(tmp_path):
    pv = ROOT / "audits/pooltogether-2024-03-holdout/contracts/src/PrizeVault.sol"
    if not pv.exists():
        import pytest
        pytest.skip("PrizeVault.sol not present")
    rel = str(pv.relative_to(ROOT))

    def _it(nm, line):
        return {"id": f"function:PrizeVault:{nm}", "kind": "function", "contract": "PrizeVault",
                "name": nm, "file": rel, "source_span": {"start_line": line}, "in_scope": True}
    manifest = {"items": [
        _it("convertToShares", 341), _it("convertToAssets", 355), _it("previewRedeem", 470),
        _it("_maxYieldVaultWithdraw", 921), _it("maxWithdraw", 404),
    ]}
    man = tmp_path / "coverage_manifest.json"
    man.write_text(json.dumps(manifest))
    out = tmp_path / "e46_audit.json"
    audit._FILE_CACHE.clear()
    sys.argv = ["erc4626_share_accounting_audit.py", "--manifest", str(man), "--out", str(out), "--quiet"]
    assert audit.main() == 0
    rep = json.loads(out.read_text())
    assert rep["routed_manifest_ids"] == [] and rep["research_only"] is True
    hit = [c for c in rep["candidates"] if c["function"] == "_maxYieldVaultWithdraw"]
    assert hit and hit[0]["confidence"] == "high", [c["function"] for c in rep["candidates"]]
