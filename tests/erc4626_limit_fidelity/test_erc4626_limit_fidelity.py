"""
Tests for the erc4626_limit_fidelity RESEARCH lens (P303). No LLM, no network.

Class: an ERC4626 wrapper's max*/limit function is not faithful to the action it bounds. Generalized from the P302
pooltogether M-02/M-03/M-07 misses. Two sub-shapes: (i-a) limit-vs-action underlying primitive mismatch; (i-b)
converted cross-basis max estimate (convertTo*(max*(...))); (ii) deposit/mint cap omits a separately-accrued
claimable.

Covers: each sub-shape fires on its synthetic positive; consistent vault (maxDeposit->deposit) is silent; a limit
with no underlying primitive is silent; a cap that subtracts the claimable is silent; convertTo*(balanceOf) (loose
co-occurrence) does NOT fire i-b; research-only flags + routed_manifest_ids == []; and a read-only pooltogether
anchor recovery (maxDeposit mismatch+cap, maxWithdraw/maxRedeem converted estimate, controlled volume).
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_context  # noqa: E402
elf = importlib.import_module("erc4626_limit_fidelity_taxonomy")
audit = importlib.import_module("erc4626_limit_fidelity_audit")


# --- pure classify_limit unit tests ---

# 1. (i-a) maxDeposit uses underlying maxDeposit but the deposit path uses mint -> mismatch
def test_primitive_mismatch_fires():
    out = elf.classify_limit("maxDeposit", "V",
                             own_body="return yieldVault.maxDeposit(address(this));",
                             resolved_body="return yieldVault.maxDeposit(address(this));",
                             deposit_actions={"mint", "previewdeposit"}, withdraw_actions=set(),
                             contract_has_claimable=False)
    shapes = {c["finding_shape"] for c in out}
    assert "erc4626_limit_action_primitive_mismatch" in shapes


# 2. (i-a) consistent vault (maxDeposit -> deposit) -> silent
def test_consistent_vault_silent():
    out = elf.classify_limit("maxDeposit", "V",
                             own_body="return yieldVault.maxDeposit(address(this));",
                             resolved_body="return yieldVault.maxDeposit(address(this));",
                             deposit_actions={"deposit"}, withdraw_actions=set(),
                             contract_has_claimable=False)
    assert out == []


# 3. (i-b) convertToAssets(maxRedeem(...)) -> converted cross-basis estimate
def test_converted_max_estimate_fires():
    body = "return yieldVault.convertToAssets(yieldVault.maxRedeem(address(this)));"
    out = elf.classify_limit("maxWithdraw", "V", own_body=body, resolved_body=body,
                             deposit_actions=set(), withdraw_actions={"redeem"}, contract_has_claimable=False)
    assert any(c["finding_shape"] == "erc4626_limit_converted_max_estimate" for c in out)


# 4. (i-b) convertToAssets(balanceOf(...)) (loose co-occurrence with a max*) -> does NOT fire
def test_converted_loose_cooccurrence_silent():
    # convertToAssets wraps balanceOf (totalAssets accounting), maxDeposit present but NOT wrapped
    body = "uint256 a = yieldVault.convertToAssets(yieldVault.balanceOf(address(this))); uint256 m = yieldVault.maxDeposit(address(this));"
    out = elf.classify_limit("maxRedeem", "V", own_body=body, resolved_body=body,
                             deposit_actions=set(), withdraw_actions={"redeem"}, contract_has_claimable=False)
    assert all(c["finding_shape"] != "erc4626_limit_converted_max_estimate" for c in out)


# 5. (ii) cap omits accrued claimable -> medium
def test_cap_omits_claimable_fires():
    out = elf.classify_limit("maxDeposit", "V",
                             own_body="uint256 lim = _twabSupplyLimit(totalSupply()); return lim;",
                             resolved_body="uint256 lim = _twabSupplyLimit(totalSupply()); return lim;",
                             deposit_actions={"deposit"}, withdraw_actions=set(), contract_has_claimable=True)
    assert any(c["finding_shape"] == "erc4626_cap_omits_accrued_claimable" for c in out)


# 6. (ii) cap that DOES reference the claimable -> silent
def test_cap_accounts_claimable_silent():
    out = elf.classify_limit("maxDeposit", "V",
                             own_body="uint256 lim = _twabSupplyLimit(totalSupply() + yieldFeeBalance); return lim;",
                             resolved_body="uint256 lim = _twabSupplyLimit(totalSupply() + yieldFeeBalance);",
                             deposit_actions={"deposit"}, withdraw_actions=set(), contract_has_claimable=True)
    assert all(c["finding_shape"] != "erc4626_cap_omits_accrued_claimable" for c in out)


# 7. limit with no underlying primitive (own-state cap, no claimable) -> silent
def test_no_underlying_silent():
    out = elf.classify_limit("maxRedeem", "V", own_body="return balanceOf(owner);",
                             resolved_body="return balanceOf(owner);",
                             deposit_actions=set(), withdraw_actions=set(), contract_has_claimable=False)
    assert out == []


# 8. vault_primitives requires a vault ref (own convertToAssets not counted)
def test_vault_primitives_requires_ref():
    assert "converttoassets" not in elf.vault_primitives("return convertToAssets(shares);")  # self method
    assert "converttoassets" in elf.vault_primitives("return yieldVault.convertToAssets(s);")


# 9. research-only flags via the runner
def test_research_only_flags(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    (tmp_path / "output" / "coverage_manifest.json").write_text(json.dumps({"schema_version": 1, "items": [
        {"id": "function:C:maxDeposit#x", "kind": "function", "contract": "C", "name": "maxDeposit",
         "file": "none.sol", "signature": "", "source_span": {"start_line": 1, "end_line": 1}, "in_scope": True}]}))
    old = sys.argv
    sys.argv = ["erc4626_limit_fidelity_audit", "--quiet"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((tmp_path / "output" / "erc4626_limit_fidelity_audit.json").read_text())
    assert r["is_gate"] is False and r["research_only"] is False and r["promotion"] == "advisory_only" and r["routes_in_production"] is False
    assert r["routed_manifest_ids"] == []


# 10. read-only pooltogether anchor recovery: all three missed classes fire, controlled volume
def test_pooltogether_anchor_recovery(monkeypatch):
    pt = ROOT / "audits" / "pooltogether-2024-03-holdout"
    if not (pt / "output" / "coverage_manifest.json").exists():
        pytest.skip("pooltogether manifest not present")
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: pt)
    audit._FILE_CACHE.clear()
    old = sys.argv
    sys.argv = ["erc4626_limit_fidelity_audit", "--manifest", str(pt / "output" / "coverage_manifest.json"), "--quiet"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((pt / "output" / "erc4626_limit_fidelity_audit.json").read_text())
    pairs = {(c["contract"], c["function"], c["finding_shape"]) for c in r["candidates"]}
    assert ("PrizeVault", "maxDeposit", "erc4626_limit_action_primitive_mismatch") in pairs   # M-03
    assert ("PrizeVault", "maxDeposit", "erc4626_cap_omits_accrued_claimable") in pairs       # M-07
    assert any(fn in ("maxWithdraw", "maxRedeem") and shp == "erc4626_limit_converted_max_estimate"
               for (_, fn, shp) in pairs)                                                      # M-02
    assert r["raw_candidates"] <= 6, f"volume not controlled: {r['raw_candidates']}"
    assert r["routes_in_production"] is False and r["routed_manifest_ids"] == []
