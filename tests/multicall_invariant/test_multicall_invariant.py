"""
Tests for the multicall_invariant RESEARCH prototype (Size Credit M-01 seed). No LLM, no network.

Covers the 4 shapes + Size M-01 recovery, the two-signal FP controls (pure-view aggregate / admin setter /
simple batch transfer / non-executing loop / thin wrapper suppressed), the needs_context demotions (unresolved
external mutators / validate-in-shared-helper), and a read-only Size end-to-end check. The detector is
research-only: is_gate:false, research_only:true, routes_in_production:false, routed_manifest_ids == [].
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
mci = importlib.import_module("multicall_invariant_taxonomy")
audit = importlib.import_module("multicall_invariant_audit")


def _shapes(name, body, sig=""):
    return {c["finding_shape"]: c["confidence"] for c in mci.classify(name, sig, "f.sol", "C", snippet=body)}


# Size M-01-style batch executor: before/after balanceOf+totalSupply around a self-delegatecall loop + validate
_M01 = """function multicall(State storage state, bytes[] calldata data) internal returns (bytes[] memory results) {
  state.data.isMulticall = true;
  uint256 borrowATokenSupplyBefore = state.data.borrowAToken.balanceOf(address(this));
  uint256 debtTokenSupplyBefore = state.data.debtToken.totalSupply();
  results = new bytes[](data.length);
  for (uint256 i = 0; i < data.length; i++) {
    results[i] = Address.functionDelegateCall(address(this), data[i]);
  }
  uint256 borrowATokenSupplyAfter = state.data.borrowAToken.balanceOf(address(this));
  uint256 debtTokenSupplyAfter = state.data.debtToken.totalSupply();
  state.validateBorrowATokenIncreaseLteDebtTokenDecrease(borrowATokenSupplyBefore, debtTokenSupplyBefore, borrowATokenSupplyAfter, debtTokenSupplyAfter);
  state.data.isMulticall = false; }"""


# 1. Size M-01 → pre_post_supply_invariant high
def test_m01_pre_post_supply_invariant_high():
    assert _shapes("multicall", _M01, "bytes[] calldata data").get("pre_post_supply_invariant") == "high"


# 2. self functionDelegateCall(address(this)) loop + supplyCap → delegatecall_self_context high
def test_delegatecall_self_context_high():
    body = """function multicall(bytes[] calldata data) external payable {
      for (uint256 i; i < data.length; i++) { Address.functionDelegateCall(address(this), data[i]); }
      require(state.supplyCap >= state.totalDeposited); }"""
    assert _shapes("multicall", body, "bytes[] calldata data").get("delegatecall_self_context") == "high"


# 3. pure-view aggregate (staticcall only, no invariant) → no candidate
def test_pure_view_aggregate_no_candidate():
    body = """function aggregate(Call[] calldata calls) external view returns (bytes[] memory results) {
      results = new bytes[](calls.length);
      for (uint256 i; i < calls.length; i++) { (, results[i]) = calls[i].target.staticcall(calls[i].callData); } }"""
    assert mci.classify("aggregate", "", "f.sol", "C", snippet=body) == []


# 4. admin batch setter (no accounting invariant) → no candidate
def test_admin_batch_setter_no_candidate():
    body = """function batchSetConfig(bytes[] calldata d) external onlyOwner {
      for (uint256 i; i < d.length; i++) { _setConfig(d[i]); } }"""
    assert mci.classify("batchSetConfig", "", "f.sol", "C", snippet=body) == []


# 5. simple batch ERC20 transfer (no invariant terms) → no candidate
def test_simple_batch_transfer_no_candidate():
    body = """function batchTransfer(address[] calldata to, uint256[] calldata amt) external {
      for (uint256 i; i < to.length; i++) { token.transfer(to[i], amt[i]); } }"""
    assert mci.classify("batchTransfer", "", "f.sol", "C", snippet=body) == []


# 6. external-call batch (opaque targets, no self/delegatecall) reading a supply invariant → needs_context (not high)
def test_external_call_batch_demotes_to_needs_context():
    body = """function batchExecute(address[] calldata targets, bytes[] calldata data) external {
      uint256 bal = token.balanceOf(address(this));
      for (uint256 i; i < targets.length; i++) { targets[i].call(data[i]); }
      require(token.balanceOf(address(this)) >= bal, "inv"); }"""
    sh = _shapes("batchExecute", body, "bytes[] calldata data")
    assert sh.get("pre_post_supply_invariant") == "needs_context"
    assert "high" not in sh.values()


# 7. per-call cap check INSIDE the loop → per_call_check_batch_bypass routes
def test_per_call_cap_check_in_loop_routes():
    body = """function multicall(bytes[] calldata data) external {
      for (uint256 i; i < data.length; i++) {
        Address.functionDelegateCall(address(this), data[i]);
        require(totalDebt <= cap, "cap");
      } }"""
    assert _shapes("multicall", body, "bytes[] calldata data").get("per_call_check_batch_bypass") in ("high", "medium")


# 8. same-tx state reuse (isMulticall flag + reusable position/balance) → same_tx_state_reuse medium+
def test_same_tx_state_reuse_routes():
    body = """function multicall(bytes[] calldata data) external {
      isMulticall = true;
      for (uint256 i; i < data.length; i++) { Address.functionDelegateCall(address(this), data[i]); }
      uint256 p = position[msg.sender]; uint256 b = token.balanceOf(address(this));
      isMulticall = false; }"""
    assert _shapes("multicall", body, "bytes[] calldata data").get("same_tx_state_reuse") in ("high", "medium")


# 9. invariant validate in a shared helper, no local before/after → demoted to needs_context
def test_validate_in_shared_helper_needs_context():
    body = """function multicall(bytes[] calldata data) external {
      uint256 s = debtToken.totalSupply();
      for (uint256 i; i < data.length; i++) { Address.functionDelegateCall(address(this), data[i]); }
      _validateInvariant(s); }"""
    sh = _shapes("multicall", body, "bytes[] calldata data")
    assert sh.get("pre_post_supply_invariant") == "needs_context"
    assert sh.get("per_call_check_batch_bypass") is None        # validate is AFTER the loop, not per-call


# 10. mutators unresolved (external loop, invariant terms, no self-delegatecall) → needs_context/medium, not high
def test_unresolved_mutators_not_high():
    body = """function batchCall(address[] calldata targets, bytes[] calldata data) external {
      uint256 capLocal = maxSupply;
      for (uint256 i; i < targets.length; i++) { targets[i].call(data[i]); }
      require(token.totalSupply() <= capLocal); }"""
    sh = _shapes("batchCall", body, "bytes[] calldata data")
    assert sh and "high" not in sh.values()
    assert sh.get("pre_post_supply_invariant") in ("needs_context", "medium")


# 11. name "multicall" but no loop/delegatecall and no invariant (thin wrapper) → no high (suppressed)
def test_thin_wrapper_no_high():
    body = "function multicall(bytes[] calldata _data) public returns (bytes[] memory) { return _impl.multicall(_data); }"
    sh = _shapes("multicall", body, "bytes[] calldata _data")
    assert "high" not in sh.values()      # suppressed entirely (no candidate) or at most low


# 12. generic numeric for-loop, no call execution → no candidate
def test_generic_numeric_loop_no_candidate():
    body = "function sumBatch(uint256[] calldata amounts) external { for (uint256 i; i < amounts.length; i++) { total += amounts[i]; } }"
    assert mci.classify("sumBatch", "", "f.sol", "C", snippet=body) == []


# 13. research-only flags
def test_research_only_flags(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    (tmp_path / "output" / "coverage_manifest.json").write_text(json.dumps({"schema_version": 1, "items": []}))
    # empty manifest raises SystemExit by design; use a 1-item manifest pointing at no source
    (tmp_path / "output" / "coverage_manifest.json").write_text(json.dumps({"schema_version": 1, "items": [
        {"id": "function:C:f#x", "kind": "function", "contract": "C", "name": "f", "file": "none.sol",
         "signature": "", "source_span": {"start_line": 1, "end_line": 1}, "in_scope": True}]}))
    old = sys.argv
    sys.argv = ["multicall_invariant_audit", "--quiet"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((tmp_path / "output" / "multicall_invariant_audit.json").read_text())
    assert r["is_gate"] is False and r["research_only"] is True and r["routes_in_production"] is False
    assert r["routed_manifest_ids"] == []


# 14. read-only Size end-to-end: M-01 recovered high; thin Size.multicall wrapper not high; 0 wrong-domain
def test_size_m01_recovery_readonly(monkeypatch):
    size = ROOT / "audits" / "size-credit-2024-06"
    if not (size / "output" / "coverage_manifest.json").exists():
        pytest.skip("Size manifest not present")
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: size)
    old = sys.argv
    sys.argv = ["multicall_invariant_audit", "--quiet"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((size / "output" / "multicall_invariant_audit.json").read_text())
    byfn = {}
    for c in r["candidates"]:
        byfn.setdefault((c["contract"], c["function"]), set()).add((c["finding_shape"], c["confidence"]))
    # M-01: the library Multicall.multicall recovered as a high pre_post_supply_invariant
    assert ("pre_post_supply_invariant", "high") in byfn.get(("Multicall", "multicall"), set())
    # the thin public wrapper is not flagged high
    assert not any(conf == "high" for _, conf in byfn.get(("Size", "multicall"), set()))
    # research-only + controlled volume + no routing
    assert r["routes_in_production"] is False and r["routed_manifest_ids"] == []
    assert r["raw_candidates"] <= 8, f"candidate volume not controlled: {r['raw_candidates']}"
