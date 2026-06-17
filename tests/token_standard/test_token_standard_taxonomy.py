"""
Tests for the token-standard taxonomy + detector (deterministic, no LLM/network).

Catches the ERC1155/721/20 surfaces behind eval misses #272 (Fertilizer NFT loss) / #273 (mint DoS),
and the FP controls keep the lens TIGHT (no Silo deposit/balanceOf/LibTransfer flood — the fishing-
expedition failure mode). Mirrors tests/cross_chain_constants.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_context  # noqa: E402
tstd = importlib.import_module("token_standard_taxonomy")
audit_mod = importlib.import_module("token_standard_audit")

F1155 = "contracts/tokens/Fertilizer/Fertilizer1155.sol"
C1155 = "Fertilizer1155"

# ── positive detection: (name, signature, file, contract, expected_standard, expected_category) ──
CATCH = [
    ("_mint", "function _mint(address to, uint256 id, uint256 amount, bytes memory data) internal", F1155, C1155, "ERC1155", "erc1155_mint"),
    ("_mintBatch", "function _mintBatch(address to, uint256[] memory ids, uint256[] memory amounts, bytes memory data) internal", F1155, C1155, "ERC1155", "erc1155_batch_mint"),
    ("safeTransferFrom", "function safeTransferFrom(address from, address to, uint256 id, uint256 amount, bytes memory data) public", F1155, C1155, "ERC1155", "erc1155_transfer"),
    ("safeBatchTransferFrom", "function safeBatchTransferFrom(address from, address to, uint256[] memory ids, uint256[] memory amounts, bytes memory data) public", F1155, C1155, "ERC1155", "erc1155_batch_transfer"),
    ("onERC1155Received", "function onERC1155Received(address, address, uint256, uint256, bytes calldata) external returns (bytes4)", "contracts/Recv.sol", "Recv", "ERC1155", "erc1155_receiver_callback"),
    ("onERC1155BatchReceived", "function onERC1155BatchReceived(address, address, uint256[] calldata, uint256[] calldata, bytes calldata) external returns (bytes4)", "contracts/Recv.sol", "Recv", "ERC1155", "erc1155_receiver_callback"),
    ("__doSafeTransferAcceptanceCheck", "function __doSafeTransferAcceptanceCheck(address operator, address from, address to, uint256 id, uint256 amount, bytes memory data) private", F1155, C1155, "ERC1155", "erc1155_acceptance_check"),
    ("setApprovalForAll", "function setApprovalForAll(address operator, bool approved) public", F1155, C1155, "ERC1155", "erc1155_approval_for_all"),
    ("isApprovedForAll", "function isApprovedForAll(address account, address operator) public view returns (bool)", F1155, C1155, "ERC1155", "erc1155_approval_for_all"),
    ("totalSupply", "function totalSupply(uint256 id) public view returns (uint256)", F1155, C1155, "ERC1155", "erc1155_supply_accounting"),
    ("uri", "function uri(uint256 id) public view returns (string memory)", F1155, C1155, "ERC1155", "erc1155_uri_metadata"),
    ("safeTransferFrom", "function safeTransferFrom(address from, address to, uint256 tokenId) public", "contracts/MyNFT.sol", "MyNFT", "ERC721", "erc721_transfer"),
    ("transferFrom", "function transferFrom(address from, address to, uint256 amount) external returns (bool)", "contracts/MockERC20.sol", "MockERC20", "ERC20", "erc20_transfer"),
    ("transferERC1155", "function transferERC1155(address token, address to, uint256 id, uint256 value) external payable", "contracts/TokenSupportFacet.sol", "TokenSupportFacet", "CUSTOM", "cross_standard_confusion"),
]


@pytest.mark.parametrize("name,sig,file,contract,std,cat", CATCH)
def test_catches_token_standard_surfaces(name, sig, file, contract, std, cat):
    c = tstd.classify(name, sig, file, contract)
    assert c["token_standard_sensitive"] is True, f"{name} should be token-standard-sensitive"
    assert c["category"] == cat, f"{name}: expected {cat}, got {c['category']}"
    assert c["standard"] == std, f"{name}: expected std {std}, got {c['standard']}"


def test_custom_wrapper_via_call_pattern():
    # a non-standard-named wrapper fn that drives an ERC1155 internally (matched via call signal)
    c = tstd.classify("processReceipt", "function processReceipt(uint256 id, uint256 amt) internal",
                      "contracts/Internalizer.sol", "Internalizer",
                      calls="IERC1155(fert).safeTransferFrom(a,b,id,amt,data)")
    assert c["token_standard_sensitive"] and c["category"] == "custom_wrapper"


def test_acceptance_check_is_high_risk():
    c = tstd.classify("__doSafeTransferAcceptanceCheck",
                      "function __doSafeTransferAcceptanceCheck(address,address,address,uint256,uint256,bytes memory) private", F1155, C1155)
    assert tstd.is_high_risk(c)


# ── FP controls: must NOT tag ──
HARMLESS = [
    ("deposit", "function deposit(uint256 amount) private", "contracts/SiloFacet.sol", "SiloFacet"),
    ("withdrawDeposit", "function withdrawDeposit(address token, int96 stem, uint256 amount, uint8 mode) external", "contracts/SiloFacet.sol", "SiloFacet"),
    ("balanceOfStalk", "function balanceOfStalk(address account) external view returns (uint256)", "contracts/SiloFacet.sol", "SiloFacet"),
    ("sow", "function sow(uint256 beans, uint256 minTemperature, LibTransfer.From mode) external payable returns (uint256)", "contracts/FieldFacet.sol", "FieldFacet"),
    ("claimFertilized", "function claimFertilized(uint256[] calldata ids, LibTransfer.To mode) external payable", "contracts/FertilizerFacet.sol", "FertilizerFacet"),
    ("transferStalk", "function transferStalk(address sender, address recipient, uint256 amount) external", "contracts/SiloFacet.sol", "SiloFacet"),
    ("transferToken", "function transferToken(IERC20 token, address recipient, uint256 amount, LibTransfer.From fromMode, LibTransfer.To toMode) external payable", "contracts/TokenFacet.sol", "TokenFacet"),
    ("tokenSettings", "function tokenSettings(address token) external view returns (bytes32)", "contracts/Whitelist.sol", "Whitelist"),
    ("getMintId", "function getMintId() internal view returns (uint256)", "contracts/Misc.sol", "Misc"),
]


@pytest.mark.parametrize("name,sig,file,contract", HARMLESS)
def test_does_not_overtag(name, sig, file, contract):
    c = tstd.classify(name, sig, file, contract)
    assert c["token_standard_sensitive"] is False, f"{name} should NOT be tagged (got {c['category']})"


def test_erc20_transfer_not_tagged_erc1155():
    c = tstd.classify("transferFrom", "function transferFrom(address from, address to, uint256 amount) external", "contracts/Erc20.sol", "Erc20")
    assert c["standard"] != "ERC1155" and c["category"] != "erc1155_transfer"


def test_erc721_transfer_not_tagged_erc1155():
    c = tstd.classify("safeTransferFrom", "function safeTransferFrom(address from, address to, uint256 tokenId) public", "contracts/MyNFT.sol", "MyNFT")
    assert c["category"] != "erc1155_transfer" and c["standard"] == "ERC721"


def test_local_id_not_token_id_accounting():
    # a function whose only token-ish signal is a param named 'id', no standard context
    c = tstd.classify("computeIndex", "function computeIndex(uint256 id) internal pure returns (uint256)", "contracts/Lib.sol", "Lib")
    assert c["token_standard_sensitive"] is False


def test_metadata_only_uri_is_low_not_transfer():
    c = tstd.classify("uri", "function uri(uint256 id) public view returns (string memory)", F1155, C1155)
    assert c["category"] == "erc1155_uri_metadata"
    assert "metadata_only" in c["risk_tags"] and not tstd.is_high_risk(c)


# ── end-to-end detector over a synthetic manifest with a cleared acceptance check ──
def test_detector_end_to_end(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    manifest = {"items": [
        {"id": "function:F:__doSafeTransferAcceptanceCheck#a", "kind": "function",
         "name": "__doSafeTransferAcceptanceCheck", "contract": "Fertilizer1155", "file": F1155,
         "signature": "function __doSafeTransferAcceptanceCheck(address,address,address,uint256,uint256,bytes memory) private",
         "source_span": {"start_line": 10}, "in_scope": True},
        {"id": "function:S:deposit#b", "kind": "function", "name": "deposit", "contract": "SiloFacet",
         "file": "contracts/SiloFacet.sol", "signature": "function deposit(uint256 amount) external",
         "source_span": {"start_line": 20}, "in_scope": True},
    ]}
    (tmp_path / "output" / "coverage_manifest.json").write_text(json.dumps(manifest))
    (tmp_path / "output" / "coverage_dispositions.json").write_text(json.dumps(
        {"dispositions": [{"manifest_id": "function:F:__doSafeTransferAcceptanceCheck#a",
                           "status": "cleared", "clear_reason": "Verbatim OZ ERC1155 acceptance-check copy"}]}))
    old = sys.argv
    sys.argv = ["token_standard_audit"]
    try:
        assert audit_mod.main() == 0
    finally:
        sys.argv = old
    rep = json.loads((tmp_path / "output" / "token_standard_audit.json").read_text())
    names = {d["name"] for d in rep["detected"]}
    assert "__doSafeTransferAcceptanceCheck" in names and "deposit" not in names  # catch + FP control
    cleared = {x["name"] for x in rep["previously_cleared_high_risk"]}
    assert "__doSafeTransferAcceptanceCheck" in cleared
    assert any(p["category"] == "erc1155_acceptance_check" for p in rep["recommended_review_packets"])
