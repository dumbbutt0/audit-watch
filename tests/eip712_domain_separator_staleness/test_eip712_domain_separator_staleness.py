"""
Tests for the eip712_domain_separator_staleness RESEARCH lens (P305). No LLM, no network.

Class: a contract caches an EIP-712 DOMAIN_SEPARATOR in the constructor from name/version, but name/version is
mutable post-construction -> cached separator is stale. Generalized from the P304 centrifuge M-03 miss.

Covers: cached-separator + post-ctor name setter -> fires; name fixed in ctor + no setter -> silent; live (per-call)
separator -> silent; library -> silent; research-only flags; read-only centrifuge anchor recovery (ERC20 fires).
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_context  # noqa: E402
eds = importlib.import_module("eip712_domain_separator_staleness_taxonomy")
audit = importlib.import_module("eip712_domain_separator_staleness_audit")


# 1. anchor-shape: immutable separator computed in ctor from name; name set later via file('name') -> high
def test_anchor_high():
    ctor = "constructor(uint8 decimals_) { decimals = decimals_; deploymentChainId = block.chainid; _DOMAIN_SEPARATOR = _calculateDomainSeparator(block.chainid); }"
    calc = ctor + " function _calculateDomainSeparator(uint256 chainId) private view returns (bytes32) { return keccak256(abi.encode(EIP712Domain, keccak256(bytes(name)), keccak256(bytes(version)), chainId, address(this))); }"
    mut = "function file(bytes32 what, string memory data) external auth { if (what == \"name\") name = data; }"
    out = eds.classify_contract("ERC20", ctor, calc, mut)
    assert out and out[0]["confidence"] == "high"
    assert out[0]["finding_shape"] == "eip712_domain_separator_staleness"


# 2. name fixed in ctor, no setter -> silent
def test_name_in_ctor_no_setter_silent():
    ctor = "constructor(string memory n) { name = n; _DOMAIN_SEPARATOR = _calculateDomainSeparator(block.chainid); }"
    calc = ctor + " function _calculateDomainSeparator(uint256 c) private view returns (bytes32){ return keccak256(abi.encode(keccak256(bytes(name)), c)); }"
    mut = "function transfer(address to, uint256 v) public returns (bool) { return true; }"
    assert eds.classify_contract("Token", ctor, calc, mut) == []


# 3. live separator (computed each call, not cached in ctor) -> silent
def test_live_separator_silent():
    ctor = "constructor() { deploymentChainId = block.chainid; }"
    calc = ctor + " function DOMAIN_SEPARATOR() external view returns (bytes32){ return keccak256(abi.encode(keccak256(bytes(name)), block.chainid)); }"
    mut = "function file(bytes32 what, string memory data) external { if (what==\"name\") name = data; }"
    assert eds.classify_contract("Token", ctor, calc, mut) == []


# 4. library -> silent
def test_library_silent():
    ctor = "constructor() { _DOMAIN_SEPARATOR = _buildDomainSeparator(); }"
    calc = ctor + " function _buildDomainSeparator() internal view returns(bytes32){return keccak256(bytes(name));}"
    assert eds.classify_contract("EIP712", ctor, calc, "function setName() external {}", kind_is_library=True) == []


# 5. cached separator but separator does NOT use name/version -> silent (S1 incomplete)
def test_separator_without_name_silent():
    ctor = "constructor() { _DOMAIN_SEPARATOR = keccak256(abi.encode(block.chainid, address(this))); }"
    assert eds.classify_contract("Token", ctor, ctor, "function setName() external { name = 'x'; }") == []


# 6. research-only flags via the runner
def test_research_only_flags(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    (tmp_path / "output" / "coverage_manifest.json").write_text(json.dumps({"schema_version": 1, "items": [
        {"id": "constructor:C:constructor#x", "kind": "constructor", "contract": "C", "name": "constructor",
         "file": "none.sol", "signature": "", "source_span": {"start_line": 1, "end_line": 1}, "in_scope": True}]}))
    old = sys.argv
    sys.argv = ["eip712_domain_separator_staleness_audit", "--quiet"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((tmp_path / "output" / "eip712_domain_separator_staleness_audit.json").read_text())
    assert r["is_gate"] is False and r["research_only"] is False and r["promotion"] == "advisory_only" and r["routes_in_production"] is False
    assert r["routed_manifest_ids"] == []


# 7. read-only centrifuge anchor recovery: ERC20 fires, controlled volume
def test_centrifuge_anchor_recovery(monkeypatch):
    cf = ROOT / "audits" / "centrifuge-2023-09-holdout"
    if not (cf / "output" / "coverage_manifest.json").exists():
        pytest.skip("centrifuge manifest not present")
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: cf)
    audit._FILE_CACHE.clear()
    old = sys.argv
    sys.argv = ["eip712_domain_separator_staleness_audit", "--manifest", str(cf / "output" / "coverage_manifest.json"), "--quiet"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((cf / "output" / "eip712_domain_separator_staleness_audit.json").read_text())
    byc = {c["contract"]: c["confidence"] for c in r["candidates"]}
    assert byc.get("ERC20") == "high"   # the anchor (M-03)
    assert r["raw_candidates"] <= 3, f"volume not controlled: {r['raw_candidates']}"
    assert r["routes_in_production"] is False and r["routed_manifest_ids"] == []
