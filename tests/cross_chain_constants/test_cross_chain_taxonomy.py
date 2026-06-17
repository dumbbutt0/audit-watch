"""
Tests for the cross-chain-sensitive constant taxonomy + detector (deterministic, no LLM/network).

Covers: the detector CATCHES the cross-chain classes that produced eval misses (BRIDGE, MERKLE_ROOT,
CHAIN_ID, HEARTBEAT, BLOCK_TIME, L1/L2 token, ORACLE_AGGREGATOR, CREATE2 salt, messenger/endpoint), and
the FP control DOES NOT over-tag harmless local constants (precision/scale, bare magic numbers, loop
counters, address(0)). Also an end-to-end detector run over a synthetic manifest.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_context  # noqa: E402
xchain = importlib.import_module("cross_chain_taxonomy")
audit_mod = importlib.import_module("cross_chain_constants_audit")


# ── catch cases: (name, signature) -> expected category ──
CATCH = [
    ("BRIDGE", "address internal constant BRIDGE = 0x4200000000000000000000000000000000000010;", "bridge"),
    ("L2_MESSENGER", "address constant L2_MESSENGER = 0x4200000000000000000000000000000000000007;", "messenger"),
    ("MERKLE_ROOT", "bytes32 constant MERKLE_ROOT = 0x1234567890123456789012345678901234567890123456789012345678901234;", "merkle_root"),
    ("CHAIN_ID", "uint256 private constant CHAIN_ID = 1;", "chain_id"),
    ("LEGACY_CHAIN_ID", "uint256 constant LEGACY_CHAIN_ID = 1;", "chain_id"),
    ("CHAINLINK_HEARTBEAT", "uint256 constant CHAINLINK_HEARTBEAT = 3600;", "heartbeat"),
    ("L1_BLOCK_TIME", "uint256 constant L1_BLOCK_TIME = 12;", "block_time"),
    ("L2_BLOCK_TIME", "uint256 constant L2_BLOCK_TIME = 2;", "block_time"),
    ("L1_BEAN", "address constant L1_BEAN = 0xBEA0000029AD1c77D3d5D23Ba2D8893dB9d1Efab;", "l1_token"),
    ("L2_BEAN", "address constant L2_BEAN = 0xBEA0000129AD1c77D3d5D23Ba2D8893dB9d1Efab;", "l2_token"),
    ("ETH_USD_CHAINLINK_PRICE_AGGREGATOR", "address constant ETH_USD_CHAINLINK_PRICE_AGGREGATOR = 0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419;", "oracle_aggregator"),
    ("BEAN_ETH_SALT", "bytes32 constant BEAN_ETH_SALT = bytes32(0);", "create2_salt"),
    ("LZ_ENDPOINT", "address constant LZ_ENDPOINT = 0x1a44076050125825900e736c501f859c50fE728c;", "endpoint"),
]


@pytest.mark.parametrize("name,sig,cat", CATCH)
def test_catches_cross_chain_classes(name, sig, cat):
    c = xchain.classify(name, sig)
    assert c["cross_chain_sensitive"] is True, f"{name} should be cross-chain-sensitive"
    assert c["category"] == cat, f"{name} expected {cat}, got {c['category']}"


def test_bridge_and_oracle_are_high_risk():
    assert xchain.is_high_risk(xchain.classify("BRIDGE", "address constant BRIDGE = 0x4200000000000000000000000000000000000010;"))
    assert xchain.is_high_risk(xchain.classify("ETH_USD_CHAINLINK_PRICE_AGGREGATOR", "address constant X = 0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419;"))


# ── FP control: harmless local constants must NOT be tagged ──
HARMLESS = [
    ("BDV_PRECISION", "uint256 constant BDV_PRECISION = 1e6;"),
    ("STALK_PER_BDV", "uint256 constant STALK_PER_BDV = 1e10;"),
    ("ONE_POINT", "uint256 constant ONE_POINT = 1e18;"),
    ("PRECISION", "uint256 constant PRECISION = 1e18;"),
    ("_PRECISION", "uint256 constant _PRECISION = 1e6;"),
    ("MAX_UINT128", "uint256 constant MAX_UINT128 = type(uint128).max;"),
    ("i", "for (uint256 i; i < n; ++i) {"),
    ("ZERO_ADDR", "address constant ZERO_ADDR = 0x0000000000000000000000000000000000000000;"),
]


@pytest.mark.parametrize("name,sig", HARMLESS)
def test_does_not_overtag_harmless(name, sig):
    c = xchain.classify(name, sig)
    assert c["cross_chain_sensitive"] is False, f"{name} should NOT be tagged (got {c['category']})"


def test_silo_roots_not_merkle():
    # 'ROOTS_BASE' must not match merkle_root via the substring 'root'
    c = xchain.classify("ROOTS_BASE", "uint256 constant ROOTS_BASE = 1e12;")
    assert c["category"] != "merkle_root"


def test_generic_hardcoded_address_tagged_but_not_high_risk():
    # a plain mainnet address with no taxonomy name still chain-specific (the EVAL-008 thesis),
    # but lands in the generic bucket, not a high-risk messaging/oracle category.
    c = xchain.classify("SOME_TOKEN", "address constant SOME_TOKEN = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;")
    assert c["cross_chain_sensitive"] is True
    assert c["category"] == "hardcoded_address"
    assert xchain.is_high_risk(c) is False


def test_l1_block_time_precedence_over_l1_token():
    # longest-name-pattern precedence: 'block_time' beats 'l1_'
    assert xchain.classify("L1_BLOCK_TIME", "uint256 constant L1_BLOCK_TIME = 12;")["category"] == "block_time"


# ── end-to-end detector over a synthetic manifest ──
def test_detector_end_to_end(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    manifest = {"items": [
        {"id": "constant:M:BRIDGE#a", "kind": "constant", "name": "BRIDGE", "contract": "M",
         "file": "contracts/M.sol", "signature": "address constant BRIDGE = 0x4200000000000000000000000000000000000010;",
         "source_span": {"start_line": 5}, "in_scope": True},
        {"id": "constant:M:BDV_PRECISION#b", "kind": "constant", "name": "BDV_PRECISION", "contract": "M",
         "file": "contracts/M.sol", "signature": "uint256 constant BDV_PRECISION = 1e6;",
         "source_span": {"start_line": 6}, "in_scope": True},
        {"id": "function:M:foo#c", "kind": "function", "name": "foo", "contract": "M",
         "file": "contracts/M.sol", "signature": "function foo() external {", "source_span": {"start_line": 9}},
    ]}
    (tmp_path / "output" / "coverage_manifest.json").write_text(json.dumps(manifest))
    # disposition: BRIDGE was cleared (the #142 lesson)
    (tmp_path / "output" / "coverage_dispositions.json").write_text(json.dumps(
        {"dispositions": [{"manifest_id": "constant:M:BRIDGE#a", "status": "cleared",
                           "clear_reason": "hardcoded bridge addr"}]}))
    old = sys.argv
    sys.argv = ["cross_chain_constants_audit"]
    try:
        assert audit_mod.main() == 0
    finally:
        sys.argv = old
    rep = json.loads((tmp_path / "output" / "cross_chain_constants_audit.json").read_text())
    names = {d["name"] for d in rep["detected"]}
    assert "BRIDGE" in names and "BDV_PRECISION" not in names           # catch + FP control
    assert rep["total_cross_chain_sensitive"] == 1
    bridge = next(d for d in rep["detected"] if d["name"] == "BRIDGE")
    assert bridge["coverage"] == "examined_but_cleared" and bridge["high_risk"] is True
    assert any(p["category"] == "bridge" for p in rep["recommended_review_packets"])
