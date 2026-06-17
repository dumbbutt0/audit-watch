"""
Tests for the connector_position_accounting lens (NOYA 2024-04 connector/TVL/position-accounting slice).
No LLM, no network.

Covers: the 3 name-gated two-signal shapes (external_reader_aggregate H-11/H-19, position_tvl_product_div
H-13, registry_key_mismatch H-12), the FP controls (name-gate, pure getter, single-term, non-TVL product/div),
the route threshold, the de-dup vs arithmetic_conservation, a fixture integration, the strict route through
advisory_escalation_gate, the prompt clear-contract, and a read-only NOYA end-to-end (4 recoveries).
"""
import hashlib
import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_context  # noqa: E402
cpa = importlib.import_module("connector_position_accounting_taxonomy")
audit = importlib.import_module("connector_position_accounting_audit")
gate = importlib.import_module("advisory_escalation_gate")

FIX_REL = "tests/fixtures/connector_position_accounting/sample.sol"
FIX = ROOT / FIX_REL
DEEP_PASS = ROOT / "prompts" / "deep_pass_packet.md"

_A1 = """function _getPositionTVL(HoldingPI memory p, address base) public view returns (uint256 tvl) {
  (uint256 totalDeposited, uint256 totalAssigned,) = proxy.getAccountCollateral(accountId, collateralType);
  tvl = _getValue(collateralType, base, totalDeposited + totalAssigned); }"""
_A2 = """function _getPositionTVL(HoldingPI memory p, address base) public view returns (uint256 tvl) {
  Market memory market = morphoBlue.market(id);
  Position memory pos = morphoBlue.position(id, address(this));
  uint256 borrowAmount = uint256(pos.borrowShares).toAssetsUp(market.totalBorrowAssets, market.totalBorrowShares);
  uint256 supplyAmount = uint256(pos.supplyShares).toAssetsUp(market.totalSupplyAssets, market.totalSupplyShares);
  tvl = _getValue(loanToken, base, supplyAmount + borrowAmount + collateral); }"""
_B = """function _getPositionTVL(HoldingPI memory p, address base) public view returns (uint256) {
  uint256 lpBalance = totalLpBalanceOf(pool);
  uint256 _totalSupply = IERC20(pool.pool).totalSupply();
  uint256 _weight = pool.weights[i];
  uint256 token1bal = valueOracle.getValue(t, base, bal);
  return (((1e18 * token1bal * lpBalance) / _weight) / _totalSupply); }"""
_C = """function updateHoldingPosition(uint256 vaultId, bytes32 _positionId, bytes calldata _data, bool removePosition) public returns (uint256) {
  bytes32 holdingPositionId = keccak256(abi.encode(msg.sender, _positionId, _data));
  uint256 positionIndex = vault.isPositionUsed[holdingPositionId];
  if (removePosition) {
    vault.isPositionUsed[keccak256(abi.encode(vault.holdingPositions[positionIndex].calculatorConnector, x, y))] = positionIndex; } }"""


# ---------------------------------------------------------------- 1-2. shape A medium/high
def test_shape_a_external_reader_aggregate_medium():
    r = cpa.classify("_getPositionTVL", "", "f.sol", "Snx", snippet=_A1)
    assert r["sensitive"] and r["shape"] == "external_reader_aggregate" and r["confidence"] == "medium"
    assert "external_position_reader" in r["signals"]


def test_shape_a_debt_mixed_high():
    r = cpa.classify("_getPositionTVL", "", "f.sol", "Morpho", snippet=_A2)
    assert r["sensitive"] and r["shape"] == "external_reader_aggregate" and r["confidence"] == "high"
    assert "debt_mixed_with_asset" in r["signals"]


# ---------------------------------------------------------------- 3. shape B product/div
def test_shape_b_position_tvl_product_div():
    r = cpa.classify("_getPositionTVL", "", "f.sol", "Balancer", snippet=_B)
    assert r["sensitive"] and r["shape"] == "position_tvl_product_div"
    assert "divide_by_weight_or_supply" in r["signals"]


# ---------------------------------------------------------------- 4. shape C registry key mismatch
def test_shape_c_registry_key_mismatch():
    r = cpa.classify("updateHoldingPosition", "", "f.sol", "Registry", snippet=_C)
    assert r["sensitive"] and r["shape"] == "registry_key_mismatch" and r["confidence"] == "medium"


# ---------------------------------------------------------------- 5-7. negatives
def test_pure_getter_not_sensitive():
    assert cpa.classify("getValue", "", "f.sol", "C",
                        snippet="function getValue(address t) external view returns(address){ return _v; }")["sensitive"] is False


def test_name_gate_excludes_non_tvl_product_div():
    # product/division but the fn name is not a TVL/value/registry name -> excluded
    assert cpa.classify("quotePrice", "", "f.sol", "C",
                        snippet="function quotePrice(uint a,uint b,uint c) public pure returns(uint){ return a*b/c; }")["sensitive"] is False


def test_tvl_single_term_no_aggregate_no_productdiv():
    r = cpa.classify("_getPositionTVL", "", "f.sol", "C",
                     snippet="function _getPositionTVL(HoldingPI memory p,address base) public view returns(uint256){ return _getValue(token, base, IERC20(token).balanceOf(address(this))); }")
    assert r["sensitive"] is False


# ---------------------------------------------------------------- 8. route threshold
def test_route_threshold():
    assert cpa.ROUTED_CONFIDENCE == {"high", "medium"}
    assert "low" not in cpa.ROUTED_CONFIDENCE


# ---------------------------------------------------------------- detector harness
def _ws(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    return tmp_path


def _line_of(needle: str) -> int:
    for i, l in enumerate(FIX.read_text().splitlines(), 1):
        if needle in l:
            return i
    raise AssertionError(f"fixture missing: {needle}")


def _item(contract, name, start, in_scope=True):
    return {"id": f"function:{contract}:{name}#x", "kind": "function", "contract": contract,
            "file": FIX_REL, "name": name, "signature": "",
            "source_span": {"start_line": start, "end_line": start}, "in_scope": in_scope,
            "attack_surface_score": 2}


def _fixture_manifest():
    # each scenario's function starts at the first line containing its unique marker
    return {"schema_version": 1, "items": [
        _item("SnxLike", "_getPositionTVL", _line_of("getAccountCollateral") - 1),
        _item("MorphoLike", "_getPositionTVL", _line_of("morphoBlue.market(id)") - 1),
        _item("BalancerLike", "_getPositionTVL", _line_of("totalLpBalanceOf(pool)") - 1),
        _item("RegistryLike", "updateHoldingPosition", _line_of("function updateHoldingPosition")),
        _item("GetterLike", "getValue", _line_of("function getValue(address t)")),
        _item("PricingLike", "quotePrice", _line_of("function quotePrice")),
        _item("SingleTermTVL", "_getPositionTVL", _line_of("contract SingleTermTVL") + 1),
    ]}


# ---------------------------------------------------------------- 9. fixture integration
def test_fixture_integration(tmp_path, monkeypatch):
    ws = _ws(tmp_path, monkeypatch)
    (ws / "output" / "coverage_manifest.json").write_text(json.dumps(_fixture_manifest()))
    old = sys.argv
    sys.argv = ["connector_position_accounting_audit"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((ws / "output" / "connector_position_accounting_audit.json").read_text())
    det = {(d["contract"], d["name"]): d for d in r["detected"]}
    assert det[("SnxLike", "_getPositionTVL")]["shape"] == "external_reader_aggregate"
    assert det[("MorphoLike", "_getPositionTVL")]["confidence"] == "high"
    assert det[("BalancerLike", "_getPositionTVL")]["shape"] == "position_tvl_product_div"
    assert det[("RegistryLike", "updateHoldingPosition")]["shape"] == "registry_key_mismatch"
    routed = set(r["routed_manifest_ids"])
    for c, n in [("SnxLike", "_getPositionTVL"), ("MorphoLike", "_getPositionTVL"),
                 ("BalancerLike", "_getPositionTVL"), ("RegistryLike", "updateHoldingPosition")]:
        assert f"function:{c}:{n}#x" in routed
    # negatives not detected
    for neg in [("GetterLike", "getValue"), ("PricingLike", "quotePrice"), ("SingleTermTVL", "_getPositionTVL")]:
        assert neg not in det
    # 4 routed of 7 in this tiny fixture; the realistic route-rate cap is asserted on NOYA (test below)
    assert len(r["routed_manifest_ids"]) == 4
    assert 0.0 <= r["route_rate"] <= 1.0


# ---------------------------------------------------------------- 10. de-dup vs arithmetic_conservation
def test_dedup_against_arithmetic_conservation(tmp_path, monkeypatch):
    ws = _ws(tmp_path, monkeypatch)
    (ws / "output" / "coverage_manifest.json").write_text(json.dumps(_fixture_manifest()))
    # arithmetic_conservation already routes the SNX-like item -> must become context_only here
    (ws / "output" / "arithmetic_conservation_audit.json").write_text(json.dumps(
        {"routed_manifest_ids": ["function:SnxLike:_getPositionTVL#x"]}))
    old = sys.argv
    sys.argv = ["connector_position_accounting_audit"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((ws / "output" / "connector_position_accounting_audit.json").read_text())
    assert "function:SnxLike:_getPositionTVL#x" not in r["routed_manifest_ids"]
    assert "function:SnxLike:_getPositionTVL#x" in r["context_only"]
    assert r["dedup_arithmetic_conservation"] >= 1
    # the others still route
    assert "function:BalancerLike:_getPositionTVL#x" in r["routed_manifest_ids"]


# ---------------------------------------------------------------- 11. strict route through advisory_escalation_gate
def test_gate_routes_connector_position_accounting_strict(tmp_path, monkeypatch):
    ws = _ws(tmp_path, monkeypatch)
    monkeypatch.setenv("AUDITWATCH_FULL_AUDIT", "1")
    mid = "function:Balancer:_getPositionTVL#x"
    (ws / "output" / "coverage_manifest.json").write_text(json.dumps({"schema_version": 1, "items": [
        {"id": mid, "kind": "function", "contract": "Balancer", "name": "_getPositionTVL",
         "file": "f.sol", "signature": "", "source_span": {"start_line": 1, "end_line": 3},
         "in_scope": True, "attack_surface_score": 2}]}))
    (ws / "output" / "coverage_dispositions.json").write_text(json.dumps({"dispositions": [
        {"manifest_id": mid, "status": "unassigned", "evidence": [], "finding_refs": []}]}))
    (ws / "output" / "connector_position_accounting_audit.json").write_text(json.dumps({"routed_manifest_ids": [mid]}))
    old = sys.argv
    sys.argv = ["advisory_escalation_gate"]
    try:
        assert gate.main() == 0
    finally:
        sys.argv = old
    disp = {d["manifest_id"]: d for d in
            json.loads((ws / "output" / "coverage_dispositions.json").read_text())["dispositions"]}
    assert disp[mid]["status"] == "assigned"
    assert disp[mid]["assigned_agent"] == "connector_position_accounting_review"


# ---------------------------------------------------------------- 12. prompt clear-contract
def test_prompt_has_connector_position_accounting_contract():
    t = " ".join(DEEP_PASS.read_text().split())
    assert "connector_position_accounting contract" in t
    assert "connector_position_accounting_review" in t
    assert "external_reader_aggregate" in t and "position_tvl_product_div" in t and "registry_key_mismatch" in t
    assert "asset-vs-liability" in t


# ---------------------------------------------------------------- 13. read-only NOYA end-to-end (4 recoveries)
def test_noya_recovers_four_misses(monkeypatch):
    noya = ROOT / "audits" / "noya-2024-04-eval"
    if not (noya / "output" / "coverage_manifest.json").exists():
        pytest.skip("NOYA manifest not present")
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: noya)
    old = sys.argv
    sys.argv = ["connector_position_accounting_audit", "--quiet"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((noya / "output" / "connector_position_accounting_audit.json").read_text())
    routed = {(d["contract"], d["name"]) for d in r["detected"] if d["manifest_id"] in r["routed_manifest_ids"]}
    assert ("SNXV3Connector", "_getPositionTVL") in routed       # H-11
    assert ("MorphoBlueConnector", "_getPositionTVL") in routed  # H-19
    assert ("BalancerConnector", "_getPositionTVL") in routed    # H-13
    assert ("PositionRegistry", "updateHoldingPosition") in routed  # H-12
    assert r["route_rate"] < 0.05
