"""
Tests for the arithmetic_conservation lens (conservation surfaces the attack-surface scorer under-weights —
Blackhole M-01 supply double-count + M-06 product-invariant rounding). No LLM, no network.

Covers: the two-signal taxonomy (shape-1 high/medium, shape-2 name-anchored), the FP controls
(accumulator / pure getter / aggregate-without-balanceOf / non-name-anchored product-division), the route
threshold, brace-matched body extraction, a fixture integration through the detector, the math_estimator
shape-2 de-dup, the strict route through advisory_escalation_gate, the prompt clear-contract, and a
read-only Blackhole M-01/M-06 end-to-end check.
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
ac = importlib.import_module("arithmetic_conservation_taxonomy")
audit = importlib.import_module("arithmetic_conservation_audit")
gate = importlib.import_module("advisory_escalation_gate")

FIX_REL = "tests/fixtures/arithmetic_conservation/sample.sol"
FIX = ROOT / FIX_REL
DEEP_PASS = ROOT / "prompts" / "deep_pass_packet.md"

_M01 = """function calculate_rebase(uint w) public view returns (uint){
  uint _veTotal = _black.balanceOf(address(_ve));
  uint _smNFTBalance = IVotingEscrow(_ve).smNFTBalance();
  uint _bonus = IVotingEscrow(_ve).bonus(_smNFTBalance);
  uint veBlackSupply = _veTotal + _smNFTBalance + _bonus;
  uint blackSupply = _black.totalSupply() + _bonus;
  uint circulatingBlack = blackSupply - veBlackSupply;
  return circulatingBlack; }"""

_K = """function _k(uint x,uint y) internal view returns(uint){
  uint _x=x*1e18/decimals0; uint _y=y*1e18/decimals1;
  uint _a=(_x*_y)/1e18; uint _b=((_x*_x)/1e18+(_y*_y)/1e18);
  return _a*_b/1e18; }"""


# ---------------------------------------------------------------- 1. shape-1 positive (M-01) → high
def test_shape1_supply_aggregate_high():
    r = ac.classify("calculate_rebase", "", "f.sol", "Minter", snippet=_M01)
    assert r["sensitive"] and r["shape"] == "supply_aggregate" and r["confidence"] == "high"
    assert "balanceof_or_totalsupply_call" in r["signals"]
    assert "supply_named" in r["signals"]


# ---------------------------------------------------------------- 2. shape-1 medium (balanceOf + aggregate, no supply name)
def test_shape1_medium_without_supply_name():
    body = """function f() public view returns(uint){
      uint a = token.balanceOf(address(this));
      uint b = pending();
      uint c = a + b - reserved;
      return c; }"""
    r = ac.classify("f", "", "f.sol", "C", snippet=body)
    assert r["sensitive"] and r["shape"] == "supply_aggregate" and r["confidence"] == "medium"


# ---------------------------------------------------------------- 3. accumulator negative (x = x + a)
def test_accumulator_not_sensitive():
    body = """function add(uint a) public {
      total = total + a; reserve = reserve + a;
      uint b = token.balanceOf(msg.sender); }"""  # has balanceOf, but only accumulator aggregates
    r = ac.classify("add", "", "f.sol", "C", snippet=body)
    assert r["sensitive"] is False


# ---------------------------------------------------------------- 4. pure getter negative
def test_pure_getter_not_sensitive():
    r = ac.classify("voter", "", "f.sol", "C", snippet="function voter() external view returns(address){ return _voter; }")
    assert r["sensitive"] is False


# ---------------------------------------------------------------- 5. aggregate WITHOUT balanceOf/supply negative
def test_plain_aggregate_without_provenance_not_sensitive():
    body = """function quote(uint amountIn, uint reserveIn) internal pure returns(uint){
      uint amtA = amountIn - reserveIn; uint fee = amountIn - amtA; return amtA - fee; }"""
    r = ac.classify("quote", "", "f.sol", "C", snippet=body)
    assert r["sensitive"] is False


# ---------------------------------------------------------------- 6. shape-2 positive (_k) → medium
def test_shape2_invariant_rounding_medium():
    r = ac.classify("_k", "", "f.sol", "Pair", snippet=_K)
    assert r["sensitive"] and r["shape"] == "invariant_rounding" and r["confidence"] == "medium"


# ---------------------------------------------------------------- 7. shape-2 NEGATIVE — not name-anchored
def test_shape2_non_name_anchored_not_sensitive():
    # product + integer division but the function is not a curve/invariant helper -> math_estimator's job
    r = ac.classify("getPrice", "", "f.sol", "C", snippet="function getPrice(uint a,uint b,uint c) public pure returns(uint){ return a*b/c; }")
    assert r["sensitive"] is False


# ---------------------------------------------------------------- 8. view kept; route threshold
def test_view_kept_and_route_threshold():
    # M-01 is `public view` and must still fire (we do NOT exclude view/pure)
    assert ac.classify("calculate_rebase", "", "f.sol", "M", snippet=_M01)["sensitive"] is True
    assert ac.ROUTED_CONFIDENCE == {"high", "medium"}
    assert "low" not in ac.ROUTED_CONFIDENCE


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
            "source_span": {"start_line": start, "end_line": start},
            "in_scope": in_scope, "attack_surface_score": 2}


def _fixture_manifest():
    return {"schema_version": 1, "source": {}, "items": [
        _item("MinterLike", "calcRebase", _line_of("function calcRebase")),
        _item("PairLike", "_k", _line_of("function _k(uint x, uint y)")),
        _item("Accum", "add", _line_of("function add(uint a, uint b)")),
        _item("Getter", "voter", _line_of("function voter()")),
        _item("Swap", "quote", _line_of("function quote(uint amountIn")),
        _item("Pricing", "getPrice", _line_of("function getPrice(uint a, uint b, uint c)")),
    ]}


# ---------------------------------------------------------------- 9. fixture integration (detector end-to-end)
def test_fixture_integration(tmp_path, monkeypatch):
    ws = _ws(tmp_path, monkeypatch)
    (ws / "output" / "coverage_manifest.json").write_text(json.dumps(_fixture_manifest()))
    old = sys.argv
    sys.argv = ["arithmetic_conservation_audit"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((ws / "output" / "arithmetic_conservation_audit.json").read_text())
    det = {(d["contract"], d["name"]): d for d in r["detected"]}

    # A. M-01 shape → high, routes calcRebase
    assert det[("MinterLike", "calcRebase")]["shape"] == "supply_aggregate"
    assert det[("MinterLike", "calcRebase")]["confidence"] == "high"
    assert "function:MinterLike:calcRebase#x" in r["routed_manifest_ids"]
    # B. M-06 shape → medium, routes _k
    assert det[("PairLike", "_k")]["shape"] == "invariant_rounding"
    assert "function:PairLike:_k#x" in r["routed_manifest_ids"]
    # C-F. negatives are not detected at all
    for neg in [("Accum", "add"), ("Getter", "voter"), ("Swap", "quote"), ("Pricing", "getPrice")]:
        assert neg not in det
    # only the two positives route; rate well under cap
    assert set(r["routed_manifest_ids"]) == {"function:MinterLike:calcRebase#x", "function:PairLike:_k#x"}
    assert r["route_rate"] < 0.5


# ---------------------------------------------------------------- 10. shape-2 de-dup against math_estimator
def test_shape2_dedup_against_math_estimator(tmp_path, monkeypatch):
    ws = _ws(tmp_path, monkeypatch)
    (ws / "output" / "coverage_manifest.json").write_text(json.dumps(_fixture_manifest()))
    # math_estimator already flagged _k → shape-2 hit must be downgraded to context_only (not routed)
    (ws / "output" / "math_estimator_audit.json").write_text(json.dumps(
        {"detected": [{"manifest_id": "function:PairLike:_k#x"}]}))
    old = sys.argv
    sys.argv = ["arithmetic_conservation_audit"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((ws / "output" / "arithmetic_conservation_audit.json").read_text())
    assert "function:PairLike:_k#x" not in r["routed_manifest_ids"]
    assert "function:PairLike:_k#x" in r["context_only"]
    assert r["dedup_math_estimator"] >= 1
    # shape-1 (M-01) is unaffected by the de-dup
    assert "function:MinterLike:calcRebase#x" in r["routed_manifest_ids"]


# ---------------------------------------------------------------- 11. strict route through advisory_escalation_gate
def test_gate_routes_arithmetic_conservation_strict(tmp_path, monkeypatch):
    ws = _ws(tmp_path, monkeypatch)
    monkeypatch.setenv("AUDITWATCH_FULL_AUDIT", "1")
    mid = "function:Minter:calculate_rebase#x"
    (ws / "output" / "coverage_manifest.json").write_text(json.dumps({"schema_version": 1, "items": [
        {"id": mid, "kind": "function", "contract": "Minter", "name": "calculate_rebase",
         "file": "f.sol", "signature": "", "source_span": {"start_line": 1, "end_line": 3},
         "in_scope": True, "attack_surface_score": 2}]}))
    (ws / "output" / "coverage_dispositions.json").write_text(json.dumps({"dispositions": [
        {"manifest_id": mid, "status": "unassigned", "evidence": [], "finding_refs": []}]}))
    (ws / "output" / "arithmetic_conservation_audit.json").write_text(json.dumps({"routed_manifest_ids": [mid]}))
    old = sys.argv
    sys.argv = ["advisory_escalation_gate"]
    try:
        assert gate.main() == 0
    finally:
        sys.argv = old
    disp = {d["manifest_id"]: d for d in
            json.loads((ws / "output" / "coverage_dispositions.json").read_text())["dispositions"]}
    assert disp[mid]["status"] == "assigned"
    assert disp[mid]["assigned_agent"] == "arithmetic_conservation_review"


# ---------------------------------------------------------------- 12. prompt clear-contract present
def test_prompt_has_arithmetic_conservation_contract():
    t = " ".join(DEEP_PASS.read_text().split())
    assert "arithmetic_conservation contract" in t
    assert "arithmetic_conservation_review" in t
    assert "already counted? y/n" in t or "already included in another term" in t
    assert "minimum-input rounding behavior" in t
    for field in ("double-count", "zero/min guard"):
        assert field in t


# ---------------------------------------------------------------- 13. read-only Blackhole M-01/M-06 end-to-end
def test_blackhole_m01_m06_route(monkeypatch):
    bh = ROOT / "audits" / "blackhole-2025-05-eval"
    if not (bh / "output" / "coverage_manifest.json").exists():
        pytest.skip("Blackhole manifest not present")
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: bh)
    old = sys.argv
    sys.argv = ["arithmetic_conservation_audit", "--quiet"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((bh / "output" / "arithmetic_conservation_audit.json").read_text())
    routed = {(d["contract"], d["name"]) for d in r["detected"] if d["manifest_id"] in r["routed_manifest_ids"]}
    assert ("MinterUpgradeable", "calculate_rebase") in routed   # M-01
    assert ("Pair", "_k") in routed                              # M-06
    assert r["route_rate"] < 0.5
