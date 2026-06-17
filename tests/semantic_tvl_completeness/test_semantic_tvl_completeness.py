"""
Tests for the semantic_tvl_completeness RESEARCH prototype (NOYA H-06/H-20 gap). No LLM, no network.

Covers the 5 finding shapes, the receiver-base equivalence + FP controls (safe gauge read, helper resolution,
transient router, claim-only, no-TVL-fn, cross-connector isolation), confidence demotion, the research-only
(no-gate / no-route) guarantee, and a read-only NOYA validation (H-06 high, H-20 medium).
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_context  # noqa: E402
stc = importlib.import_module("semantic_tvl_completeness_taxonomy")
audit = importlib.import_module("semantic_tvl_completeness_audit")

FIX_REL = "tests/fixtures/semantic_tvl_completeness/sample.sol"
FIX = ROOT / FIX_REL


# ----------------------------------------------------------------- taxonomy unit tests
def test_is_tvl_fn_gating():
    assert stc.is_tvl_fn("_getPositionTVL") and stc.is_tvl_fn("totalAssets")
    # NOT TVL readers (caused base-class / token-list noise):
    assert not stc.is_tvl_fn("_getUnderlyingTokens")
    assert not stc.is_tvl_fn("_getValue")


def test_route_confidence_constant():
    assert stc.ROUTED_CONFIDENCE == {"high", "medium"}


def test_parse_destinations_skips_router_approve_claim():
    body = """function f() public {
      IERC20(token).forceApprove(address(swapRouter), amt);
      ISwapRouter(swapRouter).swap(amt);
      IGauge(gauge).getReward(address(this)); }"""
    assert stc.parse_destinations(body) == []


def test_parse_destinations_gauge_and_pm():
    g = stc.parse_destinations("function s() public { IGauge(gauge).deposit(liq, address(this)); }")
    assert g and g[0]["kind"] == "gauge" and g[0]["base"] == "gauge"
    pm = stc.parse_destinations("function o() external { positionManager.mint(params); }")
    assert pm and pm[0]["kind"] == "position_manager"


def test_classify_omitted_external_stake_balance():
    dests = stc.parse_destinations("function s() public { IGauge(gauge).deposit(liq, address(this)); }")
    reads = stc.parse_tvl_reads("uint256 b = IERC20(pool).balanceOf(address(this)); _getValue(t, base, b);")
    cands = stc.classify_group("C", dests, reads, "_getPositionTVL")
    assert any(c["finding_shape"] == "omitted_external_stake_balance" and c["confidence"] == "high" for c in cands)


def test_receiver_base_equivalence_safe():
    # TVL reads gauge.balanceOf -> same receiver base as the gauge.deposit destination -> covered -> no candidate
    dests = stc.parse_destinations("function s() public { IGauge(gauge).deposit(liq, address(this)); }")
    reads = stc.parse_tvl_reads("uint256 s = IGauge(gauge).balanceOf(address(this));")
    assert stc.classify_group("C", dests, reads, "_getPositionTVL") == []


def test_classify_position_manager_ownership_assumption():
    dests = stc.parse_destinations("function o() external { positionManager.mint(params); }")
    reads = stc.parse_tvl_reads("(uint128 l,,,,) = pool.positions(key); (uint160 sp,,,,,,) = pool.slot0();")
    cands = stc.classify_group("C", dests, reads, "_getPositionTVL")
    assert any(c["finding_shape"] == "position_manager_ownership_assumption" and c["confidence"] == "medium"
               for c in cands)


def test_safe_uni_position_read():
    dests = stc.parse_destinations("function o() external { positionManager.mint(params); }")
    reads = stc.parse_tvl_reads("(,,,,,,, uint128 l,,,,) = positionManager.positions(tokenId);")
    assert stc.classify_group("C", dests, reads, "_getPositionTVL") == []


def test_collateral_debt_side_omission():
    dests = stc.parse_destinations("function b() public { IPool(pool).borrow(amt); }")
    reads = stc.parse_tvl_reads("uint256 b = IERC20(token).balanceOf(address(this));")
    cands = stc.classify_group("C", dests, reads, "_getPositionTVL")
    assert any(c["finding_shape"] == "collateral_debt_side_omission" for c in cands)


def test_local_balance_only_tvl():
    dests = stc.parse_destinations("function s() public { IComet(market).supply(token, amt); }")
    reads = stc.parse_tvl_reads("return IERC20(token).balanceOf(address(this));")
    cands = stc.classify_group("C", dests, reads, "_getPositionTVL")
    assert any(c["finding_shape"] == "local_balance_only_tvl" for c in cands)


def test_external_position_left_behind():
    dests = stc.parse_destinations("function s() public { IGauge(gauge).deposit(liq, address(this)); }")
    reads = stc.parse_tvl_reads("uint256 b = IERC20(pool).balanceOf(address(this));")
    cands = stc.classify_left_behind("C", True, dests, reads, "_getPositionTVL")
    assert cands and cands[0]["finding_shape"] == "external_position_left_behind"
    # with no decrease/remove entrypoint -> nothing
    assert stc.classify_left_behind("C", False, dests, reads, "_getPositionTVL") == []


def test_confidence_demotion_under_indirection():
    dests = stc.parse_destinations("function s() public { IGauge(gauge).deposit(liq, address(this)); }")
    reads = stc.parse_tvl_reads("uint256 b = IERC20(pool).balanceOf(address(this));")
    cands = stc.classify_group("C", dests, reads, "_getPositionTVL", indirection=True)
    assert cands and all(c["confidence"] == "needs_context" for c in cands)


def test_claim_only_no_destination():
    assert stc.is_claim_only("function claim() public { IGauge(gauge).getReward(address(this)); }")
    assert not stc.is_claim_only("function s() public { IGauge(gauge).deposit(liq, address(this)); }")


# ----------------------------------------------------------------- detector harness (fixture integration)
def _ws(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    return tmp_path


def _line_of(needle: str) -> int:
    for i, l in enumerate(FIX.read_text().splitlines(), 1):
        if needle in l:
            return i
    raise AssertionError(f"fixture missing: {needle}")


def _item(contract, name, start):
    return {"id": f"function:{contract}:{name}#x", "kind": "function", "contract": contract,
            "file": FIX_REL, "name": name, "signature": "",
            "source_span": {"start_line": start, "end_line": start}, "in_scope": True}


def _fixture_manifest():
    items = []
    for c in ("GaugeStakerBad", "GaugeStakerSafe", "MarketLocalOnly", "UniBad", "UniSafe",
              "HelperSafe", "ClaimOnly", "RouterOnly", "StakerNoTVL"):
        cstart = _line_of(f"contract {c}")
        # add each function defined after the contract line (simple: scan for 'function ' until next contract)
        lines = FIX.read_text().splitlines()
        i = cstart
        while i < len(lines) and not lines[i].lstrip().startswith("contract "):
            l = lines[i]
            m = l.strip()
            if m.startswith("function "):
                fn = m.split("function ", 1)[1].split("(")[0].strip()
                items.append(_item(c, fn, i + 1))
            i += 1
    return {"schema_version": 1, "items": items}


def _run(ws):
    (ws / "output" / "coverage_manifest.json").write_text(json.dumps(_fixture_manifest()))
    old = sys.argv
    sys.argv = ["semantic_tvl_completeness_audit"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    return json.loads((ws / "output" / "semantic_tvl_completeness_audit.json").read_text())


def test_fixture_integration_and_fp_controls(tmp_path, monkeypatch):
    ws = _ws(tmp_path, monkeypatch)
    r = _run(ws)
    by_contract = {}
    for c in r["candidates"]:
        by_contract.setdefault(c["connector_contract"], []).append(c["finding_shape"])
    # positives
    assert "omitted_external_stake_balance" in by_contract.get("GaugeStakerBad", [])
    assert "local_balance_only_tvl" in by_contract.get("MarketLocalOnly", [])
    assert "position_manager_ownership_assumption" in by_contract.get("UniBad", [])
    # FP controls — these must produce NO candidate
    for safe in ("GaugeStakerSafe", "UniSafe", "HelperSafe", "ClaimOnly", "RouterOnly", "StakerNoTVL"):
        assert safe not in by_contract, f"{safe} should be suppressed, got {by_contract.get(safe)}"


def test_research_only_no_gate_no_route(tmp_path, monkeypatch):
    ws = _ws(tmp_path, monkeypatch)
    r = _run(ws)
    assert r["is_gate"] is False
    assert r["research_only"] is True
    assert r["routes_in_production"] is False
    assert r["routed_manifest_ids"] == []   # default: no --research-route → nothing routed


# ----------------------------------------------------------------- read-only NOYA validation (H-06, H-20)
def test_noya_h06_h20(monkeypatch):
    noya = ROOT / "audits" / "noya-2024-04-eval"
    if not (noya / "output" / "coverage_manifest.json").exists():
        pytest.skip("NOYA manifest not present")
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: noya)
    old = sys.argv
    sys.argv = ["semantic_tvl_completeness_audit", "--quiet"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((noya / "output" / "semantic_tvl_completeness_audit.json").read_text())
    by = {(c["connector_contract"], c["finding_shape"]): c["confidence"] for c in r["candidates"]}
    assert by.get(("AerodromeConnector", "omitted_external_stake_balance")) in ("high", "medium", "needs_context")
    assert by.get(("UNIv3Connector", "position_manager_ownership_assumption")) in ("medium", "needs_context")
    assert r["routes_in_production"] is False
