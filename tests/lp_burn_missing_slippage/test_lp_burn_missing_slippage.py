"""
Tests for the lp_burn_missing_slippage RESEARCH lens (vultisig M-02 miss). No LLM, no network.

Class: a position-management function withdraws liquidity via Uniswap-V3 pool.burn()/decreaseLiquidity() and
forwards the returned amounts to a user with NO amountMin/slippage bound -> MEV-sandwichable withdrawal.

Covers: burn+LP-context+no-slippage fires; ERC20 token .burn(amount) without LP context silent; slippage-checked
silent; view silent; library silent; research-only flags; vultisig anchor recovery; size-credit FP control = 0.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_context  # noqa: E402
lbs = importlib.import_module("lp_burn_missing_slippage_taxonomy")
audit = importlib.import_module("lp_burn_missing_slippage_audit")


def _c(name, body, sig="", contract="ILOPool", kind="function"):
    return lbs.classify(name, sig, "f.sol", contract, snippet=body, kind=kind)


_LP_BURN = "{ (amount0, amount1) = pool.burn(TICK_LOWER, TICK_UPPER, liquidity2Claim); pool.collect(address(this), TICK_LOWER, TICK_UPPER, max, max); TransferHelper.safeTransfer(token0, ownerOf(tokenId), amount0); }"


# 1. LP burn + LP context + no slippage + pays user -> high
def test_lp_burn_fires_high():
    out = _c("claim", _LP_BURN, sig="function claim(uint256 tokenId) external payable returns (uint256 amount0, uint256 amount1)")
    assert out and out[0]["confidence"] == "high" and out[0]["finding_shape"] == "lp_burn_missing_slippage"


# 2. ERC20 token .burn(amount) WITHOUT uniswap LP context -> silent (no FP on debt/credit burns)
def test_erc20_burn_silent():
    body = "{ debtToken.burn(borrower, amount); credit -= amount; }"
    assert _c("repayDebt", body, sig="function repayDebt(address borrower, uint256 amount) external") == []


# 3. burn WITH an amountMin slippage bound -> silent
def test_slippage_checked_silent():
    body = "{ (amount0, amount1) = pool.burn(TICK_LOWER, TICK_UPPER, liq); require(amount0 >= amount0Min && amount1 >= amount1Min, 'slippage'); }"
    assert _c("decrease", body, sig="function decrease(uint256 amount0Min, uint256 amount1Min) external") == []


# 4. view -> silent
def test_view_silent():
    assert _c("preview", _LP_BURN, sig="function preview() external view returns (uint256 amount0)") == []


# 5. library -> silent
def test_library_silent():
    assert _c("burnHelper", _LP_BURN, sig="function burnHelper() internal", contract="LiquidityAmounts", kind="library") == []


# 6. burn but no LP context -> silent
def test_no_lp_context_silent():
    assert _c("burnIt", "{ token.burn(amount); recipient.transfer(amount); }", sig="function burnIt() external") == []


# 7. research-only flags via the runner
def test_research_only_flags(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    (tmp_path / "output" / "coverage_manifest.json").write_text(json.dumps({"schema_version": 1, "items": [
        {"id": "function:C:f#x", "kind": "function", "contract": "C", "name": "f", "file": "none.sol",
         "signature": "", "source_span": {"start_line": 1, "end_line": 1}, "in_scope": True}]}))
    old = sys.argv
    sys.argv = ["lp_burn_missing_slippage_audit", "--manifest", str(tmp_path / "output" / "coverage_manifest.json"), "--quiet", "--no-source"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((tmp_path / "output" / "lp_burn_missing_slippage_audit.json").read_text())
    assert r["is_gate"] is False and r["research_only"] is True and r["routes_in_production"] is False
    assert r["routed_manifest_ids"] == []


# 8. read-only vultisig anchor recovery: ILOPool.claim fires, volume controlled
def test_vultisig_anchor_recovery(monkeypatch):
    vt = ROOT / "audits" / "vultisig-2024-06-holdout"
    if not (vt / "output" / "coverage_manifest.json").exists():
        pytest.skip("vultisig manifest not present")
    audit._FILE_CACHE.clear()
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: vt)
    old = sys.argv
    sys.argv = ["lp_burn_missing_slippage_audit", "--manifest", str(vt / "output" / "coverage_manifest.json"), "--quiet"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((vt / "output" / "lp_burn_missing_slippage_audit.json").read_text())
    fns = {c["function"] for c in r["candidates"]}
    assert "claim" in fns
    assert r["raw_candidates"] <= 3, f"volume not controlled: {r['raw_candidates']}"
    assert r["routes_in_production"] is False and r["routed_manifest_ids"] == []


# 9. FP control: size-credit (no uniswap LP burns) -> 0 candidates
def test_size_credit_fp_control(monkeypatch):
    sc = ROOT / "audits" / "size-credit-2024-06-blind"
    if not (sc / "output" / "coverage_manifest.json").exists():
        pytest.skip("size-credit manifest not present")
    audit._FILE_CACHE.clear()
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: sc)
    old = sys.argv
    sys.argv = ["lp_burn_missing_slippage_audit", "--manifest", str(sc / "output" / "coverage_manifest.json"), "--quiet"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((sc / "output" / "lp_burn_missing_slippage_audit.json").read_text())
    assert r["raw_candidates"] == 0, f"FP on size-credit: {[(c['contract'],c['function']) for c in r['candidates']]}"
